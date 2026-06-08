from django.contrib.auth import get_user_model
User = get_user_model()
su = User.objects.filter(is_superuser=True).first()
if su:
    print(f"L'admin est: {su.email}")
    su.set_password('admin123!')
    su.save()
    print("Mot de passe reinitialise a: admin123!")
else:
    print("Aucun superuser trouve!")
