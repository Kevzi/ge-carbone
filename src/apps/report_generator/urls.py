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
    ReportEntryListView,
    ReportEntryDetailView,
    EmissionFactorPhysicalListView,
    ReportExportCSVView,
    MaterialityAssessmentDetailView,
)

urlpatterns = [
    path('', ReportListCreateView.as_view(), name='report_list_create'),
    path('<int:pk>/', ReportDetailView.as_view(), name='report_detail'),
    path('<int:pk>/status/', ReportStatusView.as_view(), name='report_status'),
    path('<int:pk>/audit-trail/', ReportAuditTrailView.as_view(), name='report_audit_trail'),
    path('<int:pk>/pdf/', ReportPDFView.as_view(), name='report_pdf'),
    path('<int:pk>/export-csv/', ReportExportCSVView.as_view(), name='report_export_csv'),
    path('<int:pk>/entries/', ReportEntryListView.as_view(), name='report_entries_list'),
    path('<int:pk>/entries/<int:entry_id>/', ReportEntryDetailView.as_view(), name='report_entry_detail'),
    path('<int:pk>/materiality-assessment/', MaterialityAssessmentDetailView.as_view(), name='materiality_assessment_detail'),
    path('emission-factors/physical/', EmissionFactorPhysicalListView.as_view(), name='emission_factors_physical'),
]
