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
    
    class Meta:
        model = Report
        fields = [
            'id', 'client_name', 'client_siret', 'fiscal_year',
            'status', 'progress_percent', 'error_message',
            'total_co2_kg', 'total_co2_tonnes',
            'scope1_co2_kg', 'scope2_co2_kg', 'scope3_co2_kg',
            'average_dqr', 'pdf_url', 'pdf_generated_at',
            'created_at', 'completed_at'
        ]
        read_only_fields = fields


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
