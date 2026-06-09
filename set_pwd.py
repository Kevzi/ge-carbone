import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ledgercarbon.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

try:
    u1 = User.objects.get(email='kevin@ledgercarbon.com')
    u1.set_password('admin123!')
    u1.save()
    print("Password set for kevin@ledgercarbon.com")
except User.DoesNotExist:
    pass

try:
    u2 = User.objects.get(email='admin@ledgercarbon.com')
    u2.set_password('admin123!')
    u2.save()
    print("Password set for admin@ledgercarbon.com")
except User.DoesNotExist:
    pass
