"""
LedgerCarbon URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from apps.carbon_engine.views import FeedbackCreateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.core.urls')),
    path('api/v1/reports/', include('apps.report_generator.urls')),
    path('api/v1/credits/', include('apps.credits.urls')),
    path('api/v1/fec/', include('apps.fec_parser.urls')),
    path('api/v1/feedback/', FeedbackCreateView.as_view(), name='carbon_feedback'),
    
    # OpenAPI endpoints
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
