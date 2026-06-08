from apps.core.models import Cabinet
from django.db import connection

cabinets_to_delete = []

for cabinet in Cabinet.objects.exclude(schema_name='public'):
    # Check if a table from a later migration exists, e.g. report_generator_report
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = '{cabinet.schema_name}' AND table_name = 'report_generator_report');")
        exists = cursor.fetchone()[0]
        if not exists:
            print(f"Cabinet {cabinet.name} ({cabinet.schema_name}) is broken. Deleting...")
            cabinets_to_delete.append(cabinet)

for cabinet in cabinets_to_delete:
    cabinet.delete(force_drop=True)

print("Cleanup done.")
