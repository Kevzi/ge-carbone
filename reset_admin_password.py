from apps.core.models import User
from django.contrib.auth import authenticate

try:
    user = User.objects.get(username="admin")
    user.set_password("admin123!")
    user.save()
    print("Password set successfully.")
    
    # Verify
    auth_user = authenticate(username="admin", password="admin123!")
    print("Authenticated successfully:", auth_user is not None)
except Exception as e:
    print("Error:", e)
