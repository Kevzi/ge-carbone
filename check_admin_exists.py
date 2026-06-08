from apps.core.models import User
print("Admin exists:", User.objects.filter(username="admin").exists())
