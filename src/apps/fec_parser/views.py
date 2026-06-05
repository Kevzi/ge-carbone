import os
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from django.conf import settings
from django.db import connection

from .serializers import FECFileUploadSerializer, FECFileSerializer
from .models import FECFile
from apps.report_generator.models import Report
from .tasks import parse_fec_file_task


class FECUploadAPIView(APIView):
    """
    API endpoint for uploading a FEC file.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = FECFileUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = serializer.validated_data['file']
        report_id = serializer.validated_data['report_id']
        
        # Verify report belongs to the user's cabinet
        try:
            report = Report.objects.get(id=report_id, cabinet=request.user.cabinet)
        except Report.DoesNotExist:
            return Response(
                {"error": "Report not found or permission denied."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check file size (max 500MB)
        max_size = getattr(settings, 'MAX_FEC_FILE_SIZE', 500 * 1024 * 1024)
        if uploaded_file.size > max_size:
            return Response(
                {"error": f"File too large. Maximum allowed size is {max_size / (1024*1024)} MB."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save file to temporary storage with secure UUID filename
        ext = os.path.splitext(uploaded_file.name)[1]
        safe_filename = f"{uuid.uuid4().hex}{ext}"
        file_name = default_storage.save(f"tmp_fec/{safe_filename}", uploaded_file)
        file_path = default_storage.path(file_name)
        file_size = os.path.getsize(file_path)
        
        # Create FECFile record
        fec_file = FECFile.objects.create(
            original_filename=uploaded_file.name,
            storage_path=file_path,
            file_size_bytes=file_size,
            validation_status='pending'
        )
        
        # Launch celery task
        schema_name = connection.schema_name
        parse_fec_file_task.delay(fec_file.id, report.id, schema_name)
        
        return Response(
            {
                "message": "File uploaded successfully and parsing started.",
                "fec_file_id": fec_file.id
            },
            status=status.HTTP_202_ACCEPTED
        )
