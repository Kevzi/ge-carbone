"""
FEC Parser serializers
"""
from rest_framework import serializers
from .models import FECFile, FECValidationRule


class FECFileUploadSerializer(serializers.Serializer):
    """Serializer for FEC file upload."""
    file = serializers.FileField()
    report_id = serializers.IntegerField()


class FECFileSerializer(serializers.ModelSerializer):
    """Serializer for FECFile model."""
    class Meta:
        model = FECFile
        fields = [
            'id', 'original_filename', 'file_size_bytes', 'row_count',
            'encoding', 'separator', 'validation_status', 'validation_errors',
            'processing_time_ms', 'created_at'
        ]
        read_only_fields = fields


class FECValidationErrorSerializer(serializers.Serializer):
    """Serializer for validation errors."""
    line_number = serializers.IntegerField()
    column = serializers.CharField()
    error_type = serializers.CharField()
    message = serializers.CharField()
    value = serializers.CharField(allow_blank=True)


class FECValidationResultSerializer(serializers.Serializer):
    """Serializer for validation result."""
    is_valid = serializers.BooleanField()
    error_count = serializers.IntegerField()
    row_count = serializers.IntegerField()
    encoding = serializers.CharField()
    separator = serializers.CharField()
    columns_found = serializers.ListField(child=serializers.CharField())
    errors = FECValidationErrorSerializer(many=True)
