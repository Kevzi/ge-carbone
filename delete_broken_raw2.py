from django.db import connection, transaction

broken_schemas = ['cabinettest1', 'cabinettest2', 'cabinettest3', 'testcabinet3']

for s in broken_schemas:
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM core_domain WHERE tenant_id IN (SELECT id FROM core_cabinet WHERE schema_name = '{s}');")
                cursor.execute(f"DELETE FROM core_user WHERE cabinet_id IN (SELECT id FROM core_cabinet WHERE schema_name = '{s}');")
                cursor.execute(f"DELETE FROM core_creditbalance WHERE cabinet_id IN (SELECT id FROM core_cabinet WHERE schema_name = '{s}');")
                cursor.execute(f"DELETE FROM core_cabinet WHERE schema_name = '{s}';")
                cursor.execute(f"DROP SCHEMA IF EXISTS {s} CASCADE;")
                print("Deleted", s)
    except Exception as e:
        print("Error deleting", s, e)
