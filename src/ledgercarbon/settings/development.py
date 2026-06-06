"""
Development settings for LedgerCarbon
"""
from .base import *

DEBUG = True

# Additional development apps (install with: pip install django-extensions)
try:
    import django_extensions  # noqa
    INSTALLED_APPS += ['django_extensions']
except ImportError:
    pass

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable HTTPS requirements
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

import sys
if 'pytest' in sys.modules or 'pytest' in sys.argv[0]:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    # For testing, combine all apps to avoid schema errors
    SHARED_APPS = list(set(SHARED_APPS + TENANT_APPS))
    if 'django_tenants' in SHARED_APPS:
        SHARED_APPS.remove('django_tenants')
    INSTALLED_APPS = SHARED_APPS
    DATABASE_ROUTERS = []
    MIDDLEWARE = [m for m in MIDDLEWARE if 'TenantMainMiddleware' not in m]
