from apps.core.models import Cabinet
broken_schemas = ['cabinettest1', 'cabinettest2', 'cabinettest3', 'testcabinet3']
for s in broken_schemas:
    try:
        c = Cabinet.objects.get(schema_name=s)
        c.delete(force_drop=True)
        print("Deleted", s)
    except Exception as e:
        print("Error deleting", s, e)
