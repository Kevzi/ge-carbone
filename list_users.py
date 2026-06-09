import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ledgercarbon.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
for u in User.objects.all():
    print(f"Email: {u.email}, Superuser: {u.is_superuser}, Active: {u.is_active}")
