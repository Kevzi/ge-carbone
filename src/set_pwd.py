import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ledgercarbon.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

try:
    u1, _ = User.objects.get_or_create(username='kevin', defaults={'email': 'kevin@ledgercarbon.com'})
    u1.set_password('SuperAdmin2026!')
    u1.is_superuser = True
    u1.is_staff = True
    u1.save()
    print("User kevin created/updated successfully with new password.")
except Exception as e:
    print(f"Error setting password: {e}")
