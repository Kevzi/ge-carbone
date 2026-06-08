from apps.core.models import User
admin = User.objects.get(username='admin')
print('Admin cabinet:', admin.cabinet.schema_name if admin.cabinet else 'None')
