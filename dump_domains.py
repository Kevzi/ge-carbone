from apps.core.models import Domain
for d in Domain.objects.all():
    print(f"Domain: {d.domain}, Tenant: {d.tenant.schema_name}")
