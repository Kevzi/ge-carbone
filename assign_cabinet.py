from django.contrib.auth import get_user_model
from apps.core.models import Cabinet
User = get_user_model()
user = User.objects.get(username='kevin')
cabinet, created = Cabinet.objects.get_or_create(name='Cabinet Test Stripe')
user.cabinet = cabinet
user.is_cabinet_admin = True
user.save()
print(f"User kevin assigned to {cabinet.name} as cabinet admin.")
