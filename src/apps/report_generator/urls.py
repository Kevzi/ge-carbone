"""
Report Generator URLs
"""
from django.urls import path
from .views import (
    ReportListCreateView,
    ReportDetailView,
    ReportStatusView,
    ReportAuditTrailView,
    ReportPDFView,
)

urlpatterns = [
    path('', ReportListCreateView.as_view(), name='report_list_create'),
    path('<int:pk>/', ReportDetailView.as_view(), name='report_detail'),
    path('<int:pk>/status/', ReportStatusView.as_view(), name='report_status'),
    path('<int:pk>/audit-trail/', ReportAuditTrailView.as_view(), name='report_audit_trail'),
    path('<int:pk>/pdf/', ReportPDFView.as_view(), name='report_pdf'),
]
