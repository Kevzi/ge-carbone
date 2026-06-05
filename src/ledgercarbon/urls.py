"""
LedgerCarbon URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.core.urls')),
    path('api/v1/reports/', include('apps.report_generator.urls')),
    path('api/v1/credits/', include('apps.credits.urls')),
    path('api/v1/fec/', include('apps.fec_parser.urls')),
]
