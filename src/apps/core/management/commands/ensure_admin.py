from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create or reset the admin superuser account'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'kevin'
        email = 'kevin@ledgercarbon.com'
        password = 'SuperAdmin2026!'

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" password reset successfully.'))
