import re
from apps.core.models import Cabinet, Domain, User, CreditBalance
from django.contrib.auth.hashers import make_password

name = "Test Cabinet 3"
schema_name = "testcabinet3"

try:
    print("Saving cabinet...")
    cabinet = Cabinet(schema_name=schema_name, name=name, plan='enterprise')
    cabinet.save()
    print("Cabinet saved successfully!")

    print("Saving domain...")
    domain = Domain(domain=f"{schema_name}.localhost", tenant=cabinet, is_primary=True)
    domain.save()
    print("Domain saved successfully!")

    print("Saving credits...")
    CreditBalance.objects.create(cabinet=cabinet, balance=100)
    print("Credits saved successfully!")

    print("Saving user...")
    admin_username = f"admin_{schema_name}"
    user = User.objects.create(
        username=admin_username,
        email=f"{admin_username}@example.com",
        password=make_password("password"),
        cabinet=cabinet,
        role="admin"
    )
    print("User saved successfully:", user.username)

except Exception as e:
    import traceback
    traceback.print_exc()
