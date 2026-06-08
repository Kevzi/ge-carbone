from apps.report_generator.models import Report
from django.db import connection
from apps.core.models import Cabinet
from django_tenants.utils import tenant_context

connection.set_schema_to_public()
print('Public reports:', Report.objects.count())

for cabinet in Cabinet.objects.exclude(schema_name='public'):
    try:
        with tenant_context(cabinet):
            print(f'Reports in {cabinet.schema_name}:', Report.objects.count())
    except Exception as e:
        print(f'Broken schema: {cabinet.schema_name}', e)
