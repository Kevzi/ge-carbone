"""
Celery tasks for report processing.
"""
from celery import shared_task
from django.utils import timezone
import logging

from .models import Report
from .services import ReportProcessingService, PDFReportGenerator, XBRLValidatorService, IXBRLGeneratorService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_report_task(self, report_id: int, fec_content_base64: str):
    """
    Celery task to process a FEC file and generate carbon report.
    
    Args:
        report_id: ID of the Report model
        fec_content_base64: Base64 encoded FEC file content
    """
    import base64
    
    try:
        report = Report.objects.get(id=report_id)
        fec_content = base64.b64decode(fec_content_base64)
        
        service = ReportProcessingService()
        success = service.process_fec(report, fec_content)
        
        if success:
            logger.info(f"Report {report_id} processed successfully")
            
            # Optionally generate PDF
            # generate_pdf_task.delay(report_id)
        else:
            logger.error(f"Report {report_id} processing failed")
            
    except Report.DoesNotExist:
        logger.error(f"Report {report_id} not found")
        
    except Exception as e:
        logger.exception(f"Error processing report {report_id}: {e}")
        
        # Retry on failure
        raise self.retry(exc=e)


@shared_task
def generate_pdf_task(report_id: int):
    """
    Celery task to generate PDF for a completed report.
    """
    try:
        report = Report.objects.get(id=report_id)
        
        if report.status != 'completed':
            logger.warning(f"Report {report_id} not completed, skipping PDF generation")
            return
        
        generator = PDFReportGenerator()
        pdf_bytes = generator.generate_pdf(report)
        
        # TODO: Upload to S3 and update report.pdf_url
        # For now, save locally
        pdf_path = f'/tmp/report_{report_id}.pdf'
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        report.pdf_url = pdf_path
        report.pdf_generated_at = timezone.now()
        report.save()
        
        logger.info(f"PDF generated for report {report_id}")
        
    except Report.DoesNotExist:
        logger.error(f"Report {report_id} not found")
        
    except Exception as e:
        logger.exception(f"Error generating PDF for report {report_id}: {e}")


@shared_task(soft_time_limit=300, time_limit=360)  # F7: 5min soft + 6min hard timeout
def validate_esrs_xbrl_task(report_id: int, file_path: str):
    """
    Celery task to run heavy Arelle XBRL validation on a generated report file.
    Takes a file path to avoid passing large Base64 payloads through the Redis broker.
    """
    import os
    import tempfile
    from pathlib import Path
    from django.core.files.storage import default_storage
    
    tmp_path = None
    try:
        report = Report.objects.get(id=report_id)
        
        # F4: Download from storage to a local temp file for Arelle
        if not default_storage.exists(file_path):
            logger.error(f"XBRL validation aborted: file does not exist in storage: {file_path}")
            return
            
        with default_storage.open(file_path, 'rb') as f:
            content = f.read()
            
        fd, tmp_path = tempfile.mkstemp(suffix='.html')
        with os.fdopen(fd, 'wb') as tmp:
            tmp.write(content)
            
        resolved = Path(tmp_path).resolve()
        
        logger.info(f"Running XBRL validation for report {report_id} on {resolved}")
        validator = XBRLValidatorService()
        is_valid, validation_results = validator.validate_file(str(resolved))
        
        report.xbrl_validation_passed = is_valid
        report.xbrl_validation_errors = validation_results
        # F5: Use update_fields to avoid race-condition clobbering concurrent task writes
        report.save(update_fields=['xbrl_validation_passed', 'xbrl_validation_errors'])
        
        if is_valid:
            logger.info(f"Report {report_id} ESEF XBRL validation PASSED.")
        else:
            logger.warning(f"Report {report_id} ESEF XBRL validation FAILED.")
            
    except Report.DoesNotExist:
        logger.error(f"Report {report_id} not found during XBRL validation")
        
    except Exception as e:
        logger.exception(f"Error during XBRL validation for report {report_id}: {e}")
        
    finally:
        # Cleanup local temp file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


@shared_task
def generate_ixbrl_task(report_id: int):
    """
    Celery task to generate iXBRL file for a completed report and trigger validation.
    """
    from django.core.files.storage import default_storage
    from django.core.files.base import ContentFile
    
    try:
        report = Report.objects.get(id=report_id)
        
        if report.status != 'completed' and report.status != 'processing':
            logger.warning(f"Report {report_id} not ready, skipping iXBRL generation")
            return
            
        # Fix Race Condition: reset validation states and mark processing
        report.status = 'processing'
        report.xbrl_validation_passed = False
        report.xbrl_validation_errors = None
        report.save(update_fields=['status', 'xbrl_validation_passed', 'xbrl_validation_errors'])
            
        generator = IXBRLGeneratorService()
        html_content = generator.generate(report)
        
        # Save to default_storage (handles local MEDIA_ROOT or S3/Azure)
        file_name = f'reports/{report.id}/ixbrl_esef.html'
        
        if default_storage.exists(file_name):
            default_storage.delete(file_name)
            
        ixbrl_path = default_storage.save(file_name, ContentFile(html_content.encode('utf-8')))
            
        report.ixbrl_url = ixbrl_path
        report.ixbrl_generated_at = timezone.now()
        report.save(update_fields=['ixbrl_url', 'ixbrl_generated_at'])
        
        logger.info(f"iXBRL generated for report {report_id}, triggering validation")
        
        # Chain with Arelle validation
        validate_esrs_xbrl_task.delay(report_id, ixbrl_path)
        
    except Report.DoesNotExist:
        logger.error(f"Report {report_id} not found during iXBRL generation")
        
    except Exception as e:
        logger.exception(f"Error generating iXBRL for report {report_id}: {e}")


@shared_task
def check_credit_alerts():
    """
    Daily task to check credit balances and send alerts.
    """
    from apps.core.models import Cabinet, CreditBalance
    
    cabinets = Cabinet.objects.all()
    
    for cabinet in cabinets:
        try:
            balance = CreditBalance.objects.get(cabinet=cabinet)
            
            if balance.balance <= cabinet.credit_alert_threshold:
                # TODO: Send email alert
                logger.info(
                    f"Credit alert for {cabinet.name}: "
                    f"{balance.balance} credits remaining "
                    f"(threshold: {cabinet.credit_alert_threshold})"
                )
                
        except CreditBalance.DoesNotExist:
            pass
