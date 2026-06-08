from django.contrib.auth import get_user_model
from apps.core.models import Cabinet
User = get_user_model()
cabinet = Cabinet.objects.first()
if cabinet:
    user = User.objects.get(username='kevin')
    user.cabinet = cabinet
    user.role = 'CABINET_ADMIN'
    user.save()
    print(f"Assigned to existing cabinet {cabinet.name}")
else:
    print("No cabinet found")
