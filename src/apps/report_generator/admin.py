"""
Report Generator admin
"""
from django.contrib import admin
from .models import Report, ReportAuditTrail


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'fiscal_year', 'status', 'total_co2_kg', 'created_at']
    list_filter = ['status', 'fiscal_year', 'created_at']
    search_fields = ['client_name', 'client_siret']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    raw_id_fields = ['cabinet', 'created_by']


@admin.register(ReportAuditTrail)
class ReportAuditTrailAdmin(admin.ModelAdmin):
    list_display = ['report', 'user', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    readonly_fields = ['report', 'user', 'action', 'details', 'ip_address', 'created_at']
