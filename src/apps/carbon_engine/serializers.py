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
    amount = serializers.ReadOnlyField()
    
    class Meta:
        model = CarbonEntry
        fields = [
            'id', 'fec_line_number', 'compte_num', 'compte_lib',
            'ecriture_lib', 'debit', 'credit', 'amount',
            'emission_factor_name', 'co2_kg', 'dqr', 'scope',
            'mapping_method'
        ]
        read_only_fields = fields
    
    def get_emission_factor_name(self, obj):
        if obj.emission_factor:
            return obj.emission_factor.name
        return 'N/A'


class CarbonEntrySummarySerializer(serializers.Serializer):
    """Serializer for aggregated carbon summary."""
    total_co2_kg = serializers.DecimalField(max_digits=15, decimal_places=2)
    scope1_co2_kg = serializers.DecimalField(max_digits=15, decimal_places=2)
    scope2_co2_kg = serializers.DecimalField(max_digits=15, decimal_places=2)
    scope3_co2_kg = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_rows = serializers.IntegerField()
    average_dqr = serializers.DecimalField(max_digits=3, decimal_places=2)
