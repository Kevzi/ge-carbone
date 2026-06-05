"""
Celery configuration for LedgerCarbon
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ledgercarbon.settings.development')

app = Celery('ledgercarbon')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


@app.task
def ping():
    """Simple ping task to verify celery worker is running."""
    return "pong"
