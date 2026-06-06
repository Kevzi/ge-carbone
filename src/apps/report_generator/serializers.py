"""
Report Generator serializers
"""
from rest_framework import serializers
from .models import Report, ReportAuditTrail


class ReportCreateSerializer(serializers.Serializer):
    """Serializer for creating a new report (with FEC upload)."""
    file = serializers.FileField()
    client_name = serializers.CharField(max_length=255)
    fiscal_year = serializers.IntegerField(min_value=2000, max_value=2100)
    client_siret = serializers.CharField(max_length=14, required=False, allow_blank=True)


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for Report model."""
    total_co2_tonnes = serializers.ReadOnlyField()
    category_breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'client_name', 'client_siret', 'fiscal_year',
            'status', 'progress_percent', 'error_message',
            'total_co2_kg', 'total_co2_tonnes',
            'scope1_co2_kg', 'scope2_co2_kg', 'scope3_co2_kg',
            'average_dqr', 'pdf_url', 'pdf_generated_at',
            'created_at', 'completed_at', 'category_breakdown',
            'xbrl_validation_passed'
        ]
        read_only_fields = fields
        
    def get_category_breakdown(self, obj):
        from django.db.models import Sum
        from apps.carbon_engine.models import CarbonEntry
        qs = CarbonEntry.objects.filter(report=obj).values('emission_factor__category', 'scope').annotate(co2=Sum('co2_kg')).order_by('-co2')
        return [
            {'category': item['emission_factor__category'] or 'Non catégorisé', 'scope': item['scope'], 'co2': item['co2']}
            for item in qs if item['co2'] > 0
        ]


class ReportStatusSerializer(serializers.ModelSerializer):
    """Serializer for report status polling."""
    class Meta:
        model = Report
        fields = ['id', 'status', 'progress_percent', 'error_message']
        read_only_fields = fields


class ReportAuditTrailSerializer(serializers.ModelSerializer):
    """Serializer for audit trail."""
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportAuditTrail
        fields = ['id', 'action', 'user_name', 'details', 'created_at']
        read_only_fields = fields
    
    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return None

class CarbonEntryUpdateSerializer(serializers.Serializer):
    """Serializer for updating physical quantity and emission factor of an entry."""
    physical_quantity = serializers.DecimalField(max_digits=15, decimal_places=4)
    physical_unit = serializers.CharField(max_length=50)
    emission_factor_id = serializers.IntegerField()

from .models import MaterialityAssessment

class MaterialityAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for the Double Materiality Questionnaire (IRO) JSON answers."""
    class Meta:
        model = MaterialityAssessment
        fields = ['id', 'report', 'data', 'created_at', 'updated_at']
        read_only_fields = ['id', 'report', 'created_at', 'updated_at']
