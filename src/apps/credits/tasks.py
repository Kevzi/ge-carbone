from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from apps.core.models import Cabinet, User
import logging

logger = logging.getLogger(__name__)

# Fallback for single-tenant mode or when django_tenants is not installed
try:
    from django_tenants.utils import schema_context
except ImportError:
    from contextlib import contextmanager
    @contextmanager
    def schema_context(schema_name):
        yield

@shared_task(bind=True, max_retries=3)
def send_low_credit_alert_task(self, cabinet_id, current_balance):
    logger.info(f"Sending low credit alert for cabinet {cabinet_id} (balance: {current_balance})")
    
    # Let Cabinet.DoesNotExist raise naturally to surface DB integrity issues
    cabinet = Cabinet.objects.get(id=cabinet_id)
    
    # Activating the schema context is critical for multi-tenant setups
    with schema_context(cabinet.schema_name):
        # Fetch admins within the schema context
        admins = User.objects.filter(cabinet=cabinet, role='admin')
        admin_emails = [admin.email for admin in admins if admin.email]
        
        if not admin_emails:
            logger.warning(f"No admin emails found for cabinet {cabinet_id}")
            return
            
        subject = "Alerte: Solde de crédits bas"
        message = (
            f"Bonjour,\n\n"
            f"Le solde de crédits de votre cabinet '{cabinet.name}' est bas.\n"
            f"Il ne vous reste que {current_balance} crédits.\n"
            f"Veuillez recharger votre solde pour éviter toute interruption de service.\n\n"
            f"L'équipe LedgerCarbon"
        )
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ledgercarbon.com')
        
        try:
            send_mail(
                subject,
                message,
                from_email,
                admin_emails,
                fail_silently=False,
            )
            logger.info(f"Sent low credit alert to {admin_emails}")
        except Exception as exc:
            logger.error(f"Error sending email for cabinet {cabinet_id}: {exc}")
            raise self.retry(exc=exc, countdown=60)
