import os
import logging
from celery import shared_task
from django_tenants.utils import schema_context
from django.utils import timezone
from .models import FECFile
from apps.report_generator.models import Report
from apps.carbon_engine.models import CarbonEntry
from .services import FECValidator, FECParser

@shared_task
def parse_fec_file_task(fec_file_id, report_id, schema_name):
    """
    Celery task to validate and parse a FEC file in streaming mode,
    then remove the original file.
    """
    logger = logging.getLogger(__name__)
    with schema_context(schema_name):
        try:
            fec_file = FECFile.objects.get(id=fec_file_id)
            report = Report.objects.get(id=report_id)
        except (FECFile.DoesNotExist, Report.DoesNotExist):
            return "File or Report not found"

        file_path = fec_file.storage_path
        
        try:
            # Update status
            report.status = 'processing'
            report.save()
            
            fec_file.validation_status = 'validating'
            fec_file.processing_started_at = timezone.now()
            fec_file.save()
            
            if not os.path.exists(file_path):
                fec_file.validation_status = 'invalid'
                fec_file.validation_errors = [{'message': 'File not found on disk'}]
                fec_file.save()
                return "File not found"
                
            # Read first few bytes for validation
            with open(file_path, 'rb') as f:
                sample_content = f.read(1024 * 1024)  # Read up to 1MB for validation
            
            validator = FECValidator()
            val_result = validator.validate(sample_content)
            
            fec_file.encoding = val_result.encoding
            fec_file.separator = val_result.separator
            
            if not val_result.is_valid:
                fec_file.validation_status = 'invalid'
                fec_file.validation_errors = [
                    {
                        'line': e.line_number, 
                        'column': e.column, 
                        'type': e.error_type, 
                        'message': e.message
                    } for e in val_result.errors
                ]
                fec_file.save()
                return "Invalid FEC format"
                
            fec_file.validation_status = 'valid'
            fec_file.save()
            
            # Start streaming parse
            parser = FECParser(chunk_size=5000)
            
            total_rows = 0
            # Open file again to stream the entire content
            with open(file_path, 'rb') as f:
                for chunk in parser.parse_streaming(f, encoding=fec_file.encoding):
                    carbon_entries = []
                    for row in chunk:
                        # Ignore rows with 0 amount ? Actually we map everything or ignore zero lines ?
                        # Create CarbonEntry
                        carbon_entries.append(
                            CarbonEntry(
                                report=report,
                                fec_line_number=row.line_number,
                                compte_num=row.compte_num,
                                compte_lib=row.compte_lib,
                                ecriture_lib=row.ecriture_lib,
                                debit=row.debit,
                                credit=row.credit,
                                co2_kg=0,  # Will be calculated by carbon_engine
                                emission_factor=None
                            )
                        )
                
                    # Bulk create for performance
                    if carbon_entries:
                        CarbonEntry.objects.bulk_create(carbon_entries)
                        total_rows += len(carbon_entries)
            
            fec_file.row_count = total_rows
            fec_file.processing_completed_at = timezone.now()
            fec_file.processing_time_ms = int((fec_file.processing_completed_at - fec_file.processing_started_at).total_seconds() * 1000)
            fec_file.save()
            
            # Optionally update report progress or status
            report.status = 'processed'
            report.save()

            # Trigger NLP enrichment task
            from apps.carbon_engine.tasks import enrich_fec_nlp_task
            enrich_fec_nlp_task.delay(report_id, schema_name)

            return f"Success: Processed {total_rows} rows."
            
        except Exception as e:
            logger.exception("Error parsing FEC file")
            fec_file.validation_status = 'invalid'
            fec_file.validation_errors = [{'message': str(e)}]
            fec_file.save()
            return f"Error: {str(e)}"
            
        finally:
            # CRITICAL: Always remove the physical file
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError:
                    logger.warning(f"Failed to remove temporary FEC file at {file_path}")
                    pass
