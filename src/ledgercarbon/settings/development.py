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
