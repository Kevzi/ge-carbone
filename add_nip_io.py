from apps.core.models import Cabinet, Domain

# Public schema domain
public_cabinet = Cabinet.objects.get(schema_name='public')
Domain.objects.get_or_create(domain='51.15.193.234.nip.io', tenant=public_cabinet, is_primary=False)

# Tenant schema domain
test_cabinet = Cabinet.objects.get(schema_name='cabinettest1')
Domain.objects.get_or_create(domain='cabinettest1.51.15.193.234.nip.io', tenant=test_cabinet, is_primary=False)

print("nip.io domains created successfully.")
