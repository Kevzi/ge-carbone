from apps.core.models import Cabinet
print([c.schema_name for c in Cabinet.objects.all()])
