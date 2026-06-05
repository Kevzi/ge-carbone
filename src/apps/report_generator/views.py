"""
Report Generator views - API endpoints for reports.
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import FileResponse
import logging

from .models import Report, ReportAuditTrail
from .serializers import (
    ReportCreateSerializer, ReportSerializer, 
    ReportStatusSerializer, ReportAuditTrailSerializer
)
from apps.fec_parser.services import FECValidator, FECParser
from apps.fec_parser.models import FECFile

logger = logging.getLogger(__name__)


class ReportListCreateView(generics.ListCreateAPIView):
    """
    GET: List all reports for the current user's cabinet
    POST: Create a new report by uploading a FEC file
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReportCreateSerializer
        return ReportSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.cabinet:
            return Report.objects.filter(cabinet=user.cabinet)
        return Report.objects.none()
    
    def create(self, request, *args, **kwargs):
        serializer = ReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uploaded_file = serializer.validated_data['file']
        client_name = serializer.validated_data['client_name']
        fiscal_year = serializer.validated_data['fiscal_year']
        client_siret = serializer.validated_data.get('client_siret', '')
        
        # Read file content
        content = uploaded_file.read()
        
        # Validate FEC
        validator = FECValidator()
        validation_result = validator.validate(content)
        
        if not validation_result.is_valid:
            return Response({
                'error': 'FEC validation failed',
                'validation': {
                    'is_valid': False,
                    'error_count': validation_result.error_count,
                    'errors': [
                        {
                            'line_number': e.line_number,
                            'column': e.column,
                            'error_type': e.error_type,
                            'message': e.message,
                        }
                        for e in validation_result.errors[:10]  # First 10 errors
                    ]
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create report
        user = request.user
        cabinet = user.cabinet
        
        # Check credits
        if cabinet:
            from apps.core.models import CreditBalance
            credit_balance, _ = CreditBalance.objects.get_or_create(
                cabinet=cabinet,
                defaults={'balance': 0}
            )
            if credit_balance.balance <= 0:
                return Response({
                    'error': 'Insufficient credits',
                    'credits_balance': credit_balance.balance
                }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
        report = Report.objects.create(
            cabinet=cabinet,
            created_by=user,
            client_name=client_name,
            client_siret=client_siret,
            fiscal_year=fiscal_year,
            status='pending'
        )
        
        # Create FEC file record
        fec_file = FECFile.objects.create(
            original_filename=uploaded_file.name,
            file_size_bytes=len(content),
            row_count=validation_result.row_count,
            encoding=validation_result.encoding,
            separator=validation_result.separator,
            validation_status='valid'
        )
        
        # Log creation
        ReportAuditTrail.objects.create(
            report=report,
            user=user,
            action='created',
            details={
                'client_name': client_name,
                'fiscal_year': fiscal_year,
                'fec_file': uploaded_file.name,
                'row_count': validation_result.row_count
            }
        )
        
        # Process FEC synchronously
        try:
            report.status = 'processing'
            report.save()
            
            ReportAuditTrail.objects.create(
                report=report,
                user=user,
                action='processing_started'
            )
            
            # Parse FEC file
            from apps.fec_parser.services import FECParser
            from apps.carbon_engine.services import CarbonCalculator
            from apps.carbon_engine.models import CarbonEntry
            from django.utils import timezone
            
            parser = FECParser()
            calculator = CarbonCalculator()
            
            rows = parser.parse_all(content)
            results = calculator.calculate_batch(rows)
            totals = calculator.aggregate_results(results)
            
            # Save carbon entries for expense accounts
            carbon_entries = []
            for result in results:
                if result.mapping_method != 'excluded' and result.co2_kg > 0:
                    carbon_entries.append(CarbonEntry(
                        report=report,
                        fec_line_number=result.fec_line_number,
                        compte_num=result.compte_num,
                        compte_lib=result.ecriture_lib[:255] if result.ecriture_lib else '',
                        debit=result.debit,
                        credit=result.credit,
                        co2_kg=result.co2_kg,
                        scope=result.scope,
                        dqr=result.dqr,
                        mapping_method=result.mapping_method
                    ))
            
            # Bulk create entries (limit to avoid memory issues)
            if carbon_entries:
                CarbonEntry.objects.bulk_create(carbon_entries[:500])
            
            # Update report with totals
            report.total_co2_kg = totals['total_co2_kg']
            report.scope1_co2_kg = totals['scope1_co2_kg']
            report.scope2_co2_kg = totals['scope2_co2_kg']
            report.scope3_co2_kg = totals['scope3_co2_kg']
            report.average_dqr = totals['average_dqr']
            report.status = 'completed'
            report.completed_at = timezone.now()
            report.save()
            
            # Deduct credit
            if cabinet:
                credit_balance.balance -= 1
                credit_balance.save()
            
            ReportAuditTrail.objects.create(
                report=report,
                user=user,
                action='processing_completed',
                details={
                    'total_co2_kg': str(totals['total_co2_kg']),
                    'rows_processed': len(rows),
                    'entries_created': len(carbon_entries)
                }
            )
            
        except Exception as e:
            logger.error(f"FEC processing failed: {e}")
            report.status = 'failed'
            report.error_message = str(e)[:500]
            report.save()
            
            ReportAuditTrail.objects.create(
                report=report,
                user=user,
                action='processing_failed',
                details={'error': str(e)[:500]}
            )
        
        return Response(
            ReportSerializer(report).data,
            status=status.HTTP_201_CREATED
        )


class ReportDetailView(generics.RetrieveAPIView):
    """
    GET: Get report details
    """
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.cabinet:
            return Report.objects.filter(cabinet=user.cabinet)
        return Report.objects.none()


class ReportStatusView(generics.RetrieveAPIView):
    """
    GET: Get report processing status (for polling)
    """
    serializer_class = ReportStatusSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.cabinet:
            return Report.objects.filter(cabinet=user.cabinet)
        return Report.objects.none()


class ReportAuditTrailView(generics.ListAPIView):
    """
    GET: Get audit trail for a report
    """
    serializer_class = ReportAuditTrailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        report_id = self.kwargs['pk']
        user = self.request.user
        
        if user.cabinet:
            report = get_object_or_404(Report, id=report_id, cabinet=user.cabinet)
            return ReportAuditTrail.objects.filter(report=report)
        
        return ReportAuditTrail.objects.none()


class ReportPDFView(APIView):
    """
    GET: Generate and download report PDF
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        user = request.user
        
        if not user.cabinet:
            return Response({'error': 'No cabinet'}, status=403)
        
        report = get_object_or_404(Report, id=pk, cabinet=user.cabinet)
        
        if report.status != 'completed':
            return Response({
                'error': 'Report not ready',
                'status': report.status
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from .services import PDFReportGenerator
            from django.http import HttpResponse
            
            generator = PDFReportGenerator()
            content = generator.generate_pdf(report)
            
            # Log download
            ReportAuditTrail.objects.create(
                report=report,
                user=user,
                action='pdf_downloaded',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            # Detect if PDF or HTML fallback
            is_pdf = content[:4] == b'%PDF'
            
            if is_pdf:
                response = HttpResponse(content, content_type='application/pdf')
                filename = f"bilan-carbone-{report.client_name}-{report.fiscal_year}.pdf"
            else:
                response = HttpResponse(content, content_type='text/html')
                filename = f"bilan-carbone-{report.client_name}-{report.fiscal_year}.html"
            
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return Response({
                'error': 'Report generation failed',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
