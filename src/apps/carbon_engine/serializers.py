"""
Carbon Engine serializers
"""
from rest_framework import serializers
from .models import EmissionFactor, CarbonEntry


class EmissionFactorSerializer(serializers.ModelSerializer):
    """Serializer for EmissionFactor."""
    class Meta:
        model = EmissionFactor
        fields = [
            'id', 'ademe_id', 'name', 'category', 'subcategory',
            'value_kg_co2_per_euro', 'unit', 'scope', 'version'
        ]
        read_only_fields = fields


class CarbonEntrySerializer(serializers.ModelSerializer):
    """Serializer for CarbonEntry."""
    emission_factor_name = serializers.SerializerMethodField()
    emission_factor_category = serializers.SerializerMethodField()
    emission_factor_value = serializers.SerializerMethodField()
    amount = serializers.ReadOnlyField()
    
    class Meta:
        model = CarbonEntry
        fields = [
            'id', 'fec_line_number', 'compte_num', 'compte_lib',
            'ecriture_lib', 'debit', 'credit', 'amount',
            'emission_factor_name', 'emission_factor_category', 'emission_factor_value', 
            'emission_factor', 'co2_kg', 'dqr', 'scope',
            'mapping_method', 'physical_quantity', 'physical_unit'
        ]
        read_only_fields = fields
    
    def _get_virtual_factor(self, obj):
        if not hasattr(self, '_mapping_service'):
            from apps.carbon_engine.services.calculator import PCGMappingService
            self._mapping_service = PCGMappingService()
        factor, _, _ = self._mapping_service.get_emission_factor(
            obj.compte_num, obj.ecriture_lib, obj.fournisseur_naf
        )
        return factor

    def get_emission_factor_name(self, obj):
        if obj.emission_factor:
            return obj.emission_factor.name
        factor = self._get_virtual_factor(obj)
        return factor.name if factor else 'Fallback moyen'

    def get_emission_factor_category(self, obj):
        if obj.emission_factor:
            return obj.emission_factor.category
        factor = self._get_virtual_factor(obj)
        return factor.category if factor else 'Fallback'

    def get_emission_factor_value(self, obj):
        if obj.emission_factor:
            return obj.emission_factor.value_kg_co2_per_euro
        factor = self._get_virtual_factor(obj)
        return factor.value_kg_co2_per_euro if factor else 0.1


class CarbonEntrySummarySerializer(serializers.Serializer):
    """Serializer for aggregated carbon summary."""
    total_co2_kg = serializers.DecimalField(max_digits=15, decimal_places=2)
    scope1_co2_kg = serializers.DecimalField(max_digits=15, decimal_places=2)
    scope2_co2_kg = serializers.DecimalField(max_digits=15, decimal_places=2)
    scope3_co2_kg = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_rows = serializers.IntegerField()
    average_dqr = serializers.DecimalField(max_digits=3, decimal_places=2)
