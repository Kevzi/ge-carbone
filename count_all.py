from apps.report_generator.models import Report
from django.db import connection
from apps.core.models import Cabinet
from django_tenants.utils import tenant_context

total_reports = 0

for cabinet in Cabinet.objects.exclude(schema_name='public'):
    try:
        with tenant_context(cabinet):
            count = Report.objects.count()
            print(f"Cabinet '{cabinet.name}' ({cabinet.schema_name}): {count} rapports")
            total_reports += count
    except Exception as e:
        pass

print(f"TOTAL: {total_reports}")
