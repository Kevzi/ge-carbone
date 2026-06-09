import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ledgercarbon.settings.local')
django.setup()

from apps.report_generator.models import Report

qs = Report.objects.none()
print("Count:", qs.count())
