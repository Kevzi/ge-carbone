"""
Report Generator services - PDF generation and report processing.
"""
import io
import logging
import os
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from arelle import CntlrCmdLine

from django.template.loader import render_to_string
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from .models import Report, ReportAuditTrail
from apps.fec_parser.services import FECParser, FECValidator
from apps.carbon_engine.services import CarbonCalculator, CarbonCalculationResult
from apps.carbon_engine.models import CarbonEntry

logger = logging.getLogger(__name__)


class ReportProcessingService:
    """
    Service for processing FEC files and generating carbon reports.
    """
    
    def __init__(self):
        self.parser = FECParser()
        self.calculator = CarbonCalculator()
    
    def process_fec(self, report: Report, fec_content: bytes) -> bool:
        """
        Process a FEC file and calculate carbon emissions.
        
        Args:
            report: Report model instance
            fec_content: Raw bytes of FEC file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update status
            report.status = 'processing'
            report.progress_percent = 0
            report.save()
            
            # Log start
            ReportAuditTrail.objects.create(
                report=report,
                user=report.created_by,
                action='processing_started',
                details={'started_at': timezone.now().isoformat()}
            )
            
            # Parse FEC
            rows = self.parser.parse_all(fec_content)
            total_rows = len(rows)
            
            # Calculate carbon for each row
            results: List[CarbonCalculationResult] = []
            
            for i, chunk in enumerate(self._chunk_rows(rows, 100)):
                chunk_results = self.calculator.calculate_batch(chunk)
                results.extend(chunk_results)
                
                # Update progress
                progress = int((i + 1) * 100 / (total_rows / 100 + 1))
                report.progress_percent = min(progress, 90)
                report.save()
            
            # Create CarbonEntry records
            self._save_carbon_entries(report, results)
            
            # Aggregate results
            totals = self.calculator.aggregate_results(results)
            
            # Update report with totals
            report.total_co2_kg = totals['total_co2_kg']
            report.scope1_co2_kg = totals['scope1_co2_kg']
            report.scope2_co2_kg = totals['scope2_co2_kg']
            report.scope3_co2_kg = totals['scope3_co2_kg']
            report.average_dqr = totals['average_dqr']
            report.status = 'completed'
            report.progress_percent = 100
            report.completed_at = timezone.now()
            report.save()
            
            # Log completion
            ReportAuditTrail.objects.create(
                report=report,
                user=report.created_by,
                action='processing_completed',
                details={
                    'total_rows': total_rows,
                    'total_co2_kg': str(report.total_co2_kg),
                    'completed_at': timezone.now().isoformat()
                }
            )
            
            return True
            
        except Exception as e:
            logger.exception(f"Error processing report {report.id}: {e}")
            
            report.status = 'failed'
            report.error_message = str(e)
            report.save()
            
            ReportAuditTrail.objects.create(
                report=report,
                user=report.created_by,
                action='processing_failed',
                details={'error': str(e)}
            )
            
            return False
    
    def _chunk_rows(self, rows, chunk_size):
        """Yield rows in chunks."""
        for i in range(0, len(rows), chunk_size):
            yield rows[i:i + chunk_size]
    
    def _save_carbon_entries(self, report: Report, results: List[CarbonCalculationResult]):
        """Save carbon entries to database."""
        entries = []
        
        for result in results:
            if result.mapping_method == 'excluded':
                continue
            
            entry = CarbonEntry(
                report=report,
                fec_line_number=result.fec_line_number,
                compte_num=result.compte_num,
                ecriture_lib=result.ecriture_lib,
                debit=result.debit,
                credit=result.credit,
                emission_factor_id=result.emission_factor_id,
                co2_kg=result.co2_kg,
                deflator_factor=result.deflator_factor,
                dqr=result.dqr,
                mapping_method=result.mapping_method,
                scope=result.scope,
                fournisseur_naf=result.fournisseur_naf,
                requires_physical_data=getattr(result, 'requires_physical_data', False)
            )
            entries.append(entry)
        
        # Bulk create for performance
        CarbonEntry.objects.bulk_create(entries, batch_size=1000)


class PDFReportGenerator:
    """
    Service for generating PDF reports.
    """
    
    def generate_html(self, report: Report) -> str:
        """
        Generate HTML content for the report.
        """
        # Get carbon entries with aggregation
        entries = CarbonEntry.objects.filter(report=report)
        
        # Aggregate by category
        category_totals = {}
        for entry in entries:
            cat = entry.emission_factor.name if entry.emission_factor else 'Autre'
            if cat not in category_totals:
                category_totals[cat] = Decimal('0')
            category_totals[cat] += entry.co2_kg
        
        # Sort by CO2 (descending)
        sorted_categories = sorted(
            category_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]  # Top 10
        
        # Handle None values
        total_co2 = report.total_co2_kg or Decimal('0')
        scope1_co2 = report.scope1_co2_kg or Decimal('0')
        scope2_co2 = report.scope2_co2_kg or Decimal('0')
        scope3_co2 = report.scope3_co2_kg or Decimal('0')
        avg_dqr = report.average_dqr or Decimal('0')
        
        context = {
            'report': report,
            'generated_at': timezone.now(),
            'total_tonnes': total_co2 / Decimal('1000') if total_co2 else Decimal('0'),
            'scope1_tonnes': scope1_co2 / Decimal('1000') if scope1_co2 else Decimal('0'),
            'scope2_tonnes': scope2_co2 / Decimal('1000') if scope2_co2 else Decimal('0'),
            'scope3_tonnes': scope3_co2 / Decimal('1000') if scope3_co2 else Decimal('0'),
            'category_totals': sorted_categories,
            'dqr_score': avg_dqr,
            'dqr_label': self._get_dqr_label(avg_dqr),
        }
        
        return render_to_string('reports/carbon_report.html', context)
    
    def _get_dqr_label(self, dqr) -> str:
        """Get human-readable DQR label."""
        if dqr is None or dqr == 0:
            dqr = 5
        if dqr <= 1.5:
            return 'Excellent'
        elif dqr <= 2.5:
            return 'Bon'
        elif dqr <= 3.5:
            return 'Moyen'
        elif dqr <= 4.5:
            return 'Faible'
        else:
            return 'Très faible'
    
    def generate_pdf(self, report: Report) -> bytes:
        """
        Generate PDF using fpdf2 (pure Python, no GTK required).
        """
        from fpdf import FPDF
        import io
        
        # Handle None values
        total_co2 = float(report.total_co2_kg or 0)
        scope1_co2 = float(report.scope1_co2_kg or 0)
        scope2_co2 = float(report.scope2_co2_kg or 0)
        scope3_co2 = float(report.scope3_co2_kg or 0)
        avg_dqr = float(report.average_dqr or 0)
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Title
        pdf.set_font('Helvetica', 'B', 24)
        pdf.set_text_color(16, 185, 129)  # Green
        pdf.cell(0, 15, 'Bilan Carbone CSRD', ln=True, align='C')
        
        # Subtitle
        pdf.set_font('Helvetica', '', 14)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 10, report.client_name, ln=True, align='C')
        pdf.cell(0, 8, f'Exercice fiscal {report.fiscal_year}', ln=True, align='C')
        
        pdf.ln(10)
        
        # Section: Emissions Summary
        pdf.set_font('Helvetica', 'B', 16)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 10, 'Synthese des emissions', ln=True)
        
        pdf.set_draw_color(226, 232, 240)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        # Emissions table
        pdf.set_font('Helvetica', '', 12)
        pdf.set_text_color(50, 50, 50)
        
        col_widths = [60, 60, 70]
        
        # Header
        pdf.set_fill_color(248, 250, 252)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(col_widths[0], 10, 'Scope', border=1, fill=True)
        pdf.cell(col_widths[1], 10, 'Emissions (kg CO2e)', border=1, fill=True)
        pdf.cell(col_widths[2], 10, 'Emissions (t CO2e)', border=1, fill=True, ln=True)
        
        pdf.set_font('Helvetica', '', 11)
        
        # Scope 1
        pdf.cell(col_widths[0], 10, 'Scope 1 - Directes', border=1)
        pdf.cell(col_widths[1], 10, f'{scope1_co2:.2f}', border=1)
        pdf.cell(col_widths[2], 10, f'{scope1_co2/1000:.2f}', border=1, ln=True)
        
        # Scope 2
        pdf.cell(col_widths[0], 10, 'Scope 2 - Energie', border=1)
        pdf.cell(col_widths[1], 10, f'{scope2_co2:.2f}', border=1)
        pdf.cell(col_widths[2], 10, f'{scope2_co2/1000:.2f}', border=1, ln=True)
        
        # Scope 3
        pdf.cell(col_widths[0], 10, 'Scope 3 - Indirectes', border=1)
        pdf.cell(col_widths[1], 10, f'{scope3_co2:.2f}', border=1)
        pdf.cell(col_widths[2], 10, f'{scope3_co2/1000:.2f}', border=1, ln=True)
        
        # Total
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_fill_color(240, 253, 244)
        pdf.cell(col_widths[0], 10, 'TOTAL', border=1, fill=True)
        pdf.cell(col_widths[1], 10, f'{total_co2:.2f}', border=1, fill=True)
        pdf.cell(col_widths[2], 10, f'{total_co2/1000:.2f}', border=1, fill=True, ln=True)
        
        pdf.ln(10)
        
        # Section: Report Info
        pdf.set_font('Helvetica', 'B', 16)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 10, 'Informations du rapport', ln=True)
        pdf.set_draw_color(226, 232, 240)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font('Helvetica', '', 11)
        pdf.set_text_color(50, 50, 50)
        
        pdf.cell(50, 8, 'Client:', ln=False)
        pdf.cell(0, 8, report.client_name, ln=True)
        
        pdf.cell(50, 8, 'SIRET:', ln=False)
        pdf.cell(0, 8, report.client_siret or '-', ln=True)
        
        pdf.cell(50, 8, 'Score qualite (DQR):', ln=False)
        pdf.cell(0, 8, f'{avg_dqr:.1f}/5 - {self._get_dqr_label(avg_dqr)}', ln=True)
        
        pdf.cell(50, 8, 'Date de creation:', ln=False)
        pdf.cell(0, 8, report.created_at.strftime('%d/%m/%Y %H:%M'), ln=True)
        
        pdf.ln(10)
        
        # Footer
        pdf.set_font('Helvetica', 'I', 9)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 8, 'Rapport genere par LedgerCarbon - Solution SaaS de reporting CSRD', ln=True, align='C')
        pdf.cell(0, 6, 'Emissions exprimees en equivalent CO2 selon GHG Protocol et ADEME', ln=True, align='C')
        
        # Log PDF generation
        try:
            ReportAuditTrail.objects.create(
                report=report,
                user=report.created_by,
                action='pdf_generated',
                details={'generated_at': timezone.now().isoformat()}
            )
        except Exception:
            pass
        
        # Return PDF bytes
        return pdf.output()

class XBRLValidatorService:
    """
    Validates iXBRL / XBRL documents against the EFRAG ESRS taxonomy
    using the Arelle open-source engine.
    """
    
    # Official EFRAG Set 1 Entry Point — ESRS Set 1 published by EFRAG
    ESRS_ENTRY_POINT = "https://xbrl.efrag.org/taxonomy/esrs/2023-12-22/esrs_all.xsd"
    
    # Maximum number of errors stored to prevent enormous JSONField rows
    MAX_ERRORS = 100

    def __init__(self):
        """
        Initialize the Arelle controller.
        """
        # Arelle manages its own controller via parseAndRun
        pass
    
    def validate_file(self, file_path: str) -> tuple[bool, dict]:
        """
        Runs Arelle validation on the provided XBRL/iXBRL file.
        
        Args:
            file_path: Absolute path to the generated iXBRL file.
            
        Returns:
            Tuple (is_valid, error_details_dict)
        """
        logger.info(f"Starting Arelle ESRS validation for: {file_path}")
        
        from arelle.CntlrCmdLine import parseAndRun
        
        # F2 fix: use two separate tokens for argparse compatibility
        # F1 fix: pass the official EFRAG ESRS entry point as the taxonomy source
        try:
            cntlr = parseAndRun([
                "--file", file_path,
                "--import", self.ESRS_ENTRY_POINT,
                "--formula", "run",
                "--validate",
                "--logFormat", "[%(messageCode)s] %(message)s - %(file)s"
            ])
        except SystemExit as e:
            logger.error(f"Arelle parseAndRun triggered SystemExit({e.code})")
            return False, {
                "errors": [{"code": "SYSTEM_EXIT", "message": f"Arelle fatal error (exit code {e.code})", "file": file_path}],
                "warnings": [],
                "validation_timestamp": None
            }
        
        errors = []
        is_valid = True
        
        if hasattr(cntlr, 'logHandler'):
            for log_rec in getattr(cntlr.logHandler, 'logRecordBuffer', []):
                if log_rec.levelno >= logging.ERROR:
                    msg_code = getattr(log_rec, 'messageCode', 'UNKNOWN')
                    if not msg_code.startswith('ea_'):
                        is_valid = False
                    # F8 fix: cap errors list to avoid unbounded JSONField rows
                    if len(errors) < self.MAX_ERRORS:
                        errors.append({
                            "code": msg_code,
                            "message": log_rec.getMessage(),
                            "file": getattr(log_rec, 'file', file_path)
                        })
        
        truncated = len(getattr(getattr(cntlr, 'logHandler', None), 'logRecordBuffer', [])) > self.MAX_ERRORS
        
        result_details = {
            "total_errors": len(errors),
            "errors_truncated": truncated,
            "errors": errors,
            "validated_against": self.ESRS_ENTRY_POINT,
            "exit_code": 0 if is_valid else 1
        }
        
        if not is_valid:
            logger.warning(f"Validation FAILED with {len(errors)} error(s).")
        else:
            logger.info("Validation PASSED successfully.")
            
        return is_valid, result_details

class IXBRLGeneratorService:
    """
    Service for generating iXBRL files from a Carbon Report and Materiality Assessment.
    """
    
    def generate(self, report: Report) -> str:
        """
        Generates the iXBRL HTML string for a given report.
        
        Args:
            report: The Report instance.
            
        Returns:
            str: The rendered XHTML containing iXBRL inline tags.
        """
        logger.info(f"Generating iXBRL for report {report.id}")
        
        try:
            materiality = report.materiality_assessment
        except ObjectDoesNotExist:
            materiality = None
            
        context = {
            'report': report,
            'materiality': materiality
        }
        
        html_string = render_to_string('reports/ixbrl_template.html', context)
        return html_string

