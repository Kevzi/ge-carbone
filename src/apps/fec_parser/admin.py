"""
FEC Parser admin
"""
from django.contrib import admin
from .models import FECFile, FECValidationRule


@admin.register(FECFile)
class FECFileAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'row_count', 'validation_status', 'created_at']
    list_filter = ['validation_status', 'created_at']
    search_fields = ['original_filename']
    readonly_fields = ['created_at', 'updated_at', 'processing_time_ms']


@admin.register(FECValidationRule)
class FECValidationRuleAdmin(admin.ModelAdmin):
    list_display = ['column_name', 'column_index', 'is_required', 'data_type']
    list_filter = ['is_required', 'data_type']
    ordering = ['column_index']
