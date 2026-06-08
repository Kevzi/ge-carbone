from apps.core.models import User
try:
    admin = User.objects.get(username='admin')
    print('Admin exists:', admin.username)
    print('Admin is_active:', admin.is_active)
    print('Admin is_superuser:', admin.is_superuser)
    print('Admin has usable password:', admin.has_usable_password())
except User.DoesNotExist:
    print('Admin does not exist!')
