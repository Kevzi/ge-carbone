"""
Carbon Engine admin
"""
from django.contrib import admin
from .models import EmissionFactor, PCGMapping, CarbonEntry


@admin.register(EmissionFactor)
class EmissionFactorAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'value_kg_co2_per_euro', 'scope', 'version']
    list_filter = ['scope', 'category', 'version']
    search_fields = ['name', 'category', 'ademe_id']


@admin.register(PCGMapping)
class PCGMappingAdmin(admin.ModelAdmin):
    list_display = ['pcg_prefix', 'emission_factor', 'priority']
    list_filter = ['priority']
    search_fields = ['pcg_prefix', 'pcg_description']
    raw_id_fields = ['emission_factor']


@admin.register(CarbonEntry)
class CarbonEntryAdmin(admin.ModelAdmin):
    list_display = ['report', 'fec_line_number', 'compte_num', 'co2_kg', 'dqr', 'scope']
    list_filter = ['scope', 'dqr', 'mapping_method']
    search_fields = ['compte_num', 'ecriture_lib']
    raw_id_fields = ['report', 'emission_factor']
