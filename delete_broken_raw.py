from django.db import connection

broken_schemas = ['cabinettest1', 'cabinettest2', 'cabinettest3', 'testcabinet3']

with connection.cursor() as cursor:
    for s in broken_schemas:
        try:
            # Delete from core_cabinet table directly to bypass Django ORM cascade
            cursor.execute(f"DELETE FROM core_domain WHERE tenant_id IN (SELECT id FROM core_cabinet WHERE schema_name = '{s}');")
            cursor.execute(f"DELETE FROM core_user WHERE cabinet_id IN (SELECT id FROM core_cabinet WHERE schema_name = '{s}');")
            cursor.execute(f"DELETE FROM credits_creditbalance WHERE cabinet_id IN (SELECT id FROM core_cabinet WHERE schema_name = '{s}');")
            cursor.execute(f"DELETE FROM core_cabinet WHERE schema_name = '{s}';")
            
            # Drop the schema
            cursor.execute(f"DROP SCHEMA IF EXISTS {s} CASCADE;")
            print("Deleted", s)
        except Exception as e:
            print("Error deleting", s, e)
