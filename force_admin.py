from django.contrib.auth import get_user_model
User = get_user_model()
try:
    user = User.objects.get(username='kevin')
    user.set_password('kevin2024!')
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print("User kevin updated.")
except User.DoesNotExist:
    user = User.objects.create_superuser('kevin', 'kevin@ledgercarbon.com', 'kevin2024!')
    print("User kevin created.")
