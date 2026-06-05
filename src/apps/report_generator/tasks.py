"""
Celery tasks for report processing.
"""
from celery import shared_task
from django.utils import timezone
import logging

from .models import Report
from .services import ReportProcessingService, PDFReportGenerator

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
