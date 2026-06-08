from django.conf import settings
from django.core.files.storage import default_storage

print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"Storage location: {getattr(default_storage, 'location', 'N/A')}")
print(f"Storage base_url: {getattr(default_storage, 'base_url', 'N/A')}")
