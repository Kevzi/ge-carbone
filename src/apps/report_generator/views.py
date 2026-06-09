"""
Report Generator views - API endpoints for reports.
"""
from rest_framework import generics, status, permissions, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.http import FileResponse, StreamingHttpResponse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.utils.text import slugify
from django.db import IntegrityError
from django.http import Http404
import logging
import csv
import io

from .models import Report, ReportAuditTrail, MaterialityAssessment
from .serializers import (
    ReportCreateSerializer, ReportSerializer, 
    ReportStatusSerializer, ReportAuditTrailSerializer,
    CarbonEntryUpdateSerializer, MaterialityAssessmentSerializer
)
from apps.fec_parser.services import FECValidator, FECParser
from apps.fec_parser.models import FECFile
from apps.carbon_engine.models import CarbonEntry, EmissionFactor
from apps.carbon_engine.serializers import CarbonEntrySerializer, EmissionFactorSerializer

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
            status='pending',
            total_energy_mwh=0
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
            
            rows = parser.parse_all(io.BytesIO(content))
            results = calculator.calculate_batch(rows)
            totals = calculator.aggregate_results(results)
            
            # Save carbon entries for expense accounts
            carbon_entries = []
            for result in results:
                needs_physical = getattr(result, 'requires_physical_data', False)
                if result.mapping_method != 'excluded' and (result.co2_kg > 0 or needs_physical):
                    carbon_entries.append(CarbonEntry(
                        report=report,
                        fec_line_number=result.fec_line_number,
                        ecriture_date=result.ecriture_date,
                        ecriture_lib=result.ecriture_lib,
                        compte_num=result.compte_num,
                        compte_lib=result.ecriture_lib[:255] if result.ecriture_lib else '',
                        debit=result.debit,
                        credit=result.credit,
                        co2_kg=result.co2_kg,
                        scope=result.scope,
                        dqr=result.dqr,
                        mapping_method=result.mapping_method,
                        requires_physical_data=needs_physical
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


class ReportDetailView(generics.RetrieveDestroyAPIView):
    """
    GET: Get report details
    DELETE: Delete a report
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
            return ReportAuditTrail.objects.filter(report=report).order_by('-created_at')
        
        return ReportAuditTrail.objects.none()


class ReportEntryPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000

class ReportEntryListView(generics.ListAPIView):
    """
    List CarbonEntries for a given report, with filtering and pagination.
    """
    serializer_class = CarbonEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ReportEntryPagination
    
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['co2_kg', 'fec_line_number', 'amount']
    ordering = ['fec_line_number']
    filterset_fields = ['scope', 'emission_factor__category']
    
    def get_queryset(self):
        report_id = self.kwargs['pk']
        user = self.request.user
        
        if not user.cabinet:
            raise PermissionDenied('No cabinet associated with this user')
            
        report = get_object_or_404(Report, id=report_id, cabinet=user.cabinet)
        qs = CarbonEntry.objects.filter(report=report).select_related('emission_factor')
        
        # Custom category filter support for ?category=
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(emission_factor__category=category)
            
        # Support for pending physical data
        pending_physical = self.request.query_params.get('pending_physical')
        if pending_physical == 'true':
            qs = qs.filter(requires_physical_data=True, physical_quantity__isnull=True)
            
        return qs


class ReportEntryDetailView(APIView):
    """
    PATCH: Update a carbon entry's physical quantity and emission factor
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, pk, entry_id):
        user = request.user
        if not user.cabinet:
            return Response({'error': 'No cabinet'}, status=status.HTTP_403_FORBIDDEN)
            
        report = get_object_or_404(Report, id=pk, cabinet=user.cabinet)
        entry = get_object_or_404(CarbonEntry, id=entry_id, report=report)
        
        serializer = CarbonEntryUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        validated_data = serializer.validated_data
        physical_quantity = validated_data.get('physical_quantity')
        physical_unit = validated_data.get('physical_unit')
        emission_factor_id = validated_data.get('emission_factor_id')
        
        if physical_quantity is None or not physical_unit or not emission_factor_id:
            return Response({'error': 'Missing required fields for physical update'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure emission factor exists
        new_factor = get_object_or_404(EmissionFactor, id=emission_factor_id)
        
        if new_factor.value_kg_co2_per_unit is None:
            return Response({
                'error': 'Le facteur d\'émission sélectionné n\'a pas de valeur par unité physique.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Avoid spamming audit logs
        if (entry.physical_quantity == physical_quantity and 
            entry.physical_unit == physical_unit and 
            entry.emission_factor_id == new_factor.id):
            return Response(CarbonEntrySerializer(entry).data)
        
        # Calculate new CO2 and log via service
        from apps.carbon_engine.services.calculator import CarbonCalculator
        calculator = CarbonCalculator()
        try:
            calculator.update_entry_physically(entry, physical_quantity, physical_unit, new_factor, user)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        entry.refresh_from_db()
        return Response(CarbonEntrySerializer(entry).data)




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
            
        if report.has_pending_physical_data:
            return Response(
                {"error": "Saisie physique incomplète. Vous devez compléter les quantités physiques avant de générer le PDF."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check and deduct credit
        from apps.credits.services import CreditService
        credit_service = CreditService()
        success, error_msg = credit_service.deduct_credit_for_report(report, user=user)
        if not success:
            return Response({
                'error': 'Insufficient credits',
                'detail': error_msg
            }, status=status.HTTP_402_PAYMENT_REQUIRED)
        
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
                response = HttpResponse(bytes(content), content_type='application/pdf')
                filename = f"bilan-carbone-{report.client_name}-{report.fiscal_year}.pdf"
            else:
                response = HttpResponse(bytes(content), content_type='text/html')
                filename = f"bilan-carbone-{report.client_name}-{report.fiscal_year}.html"
            
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return Response({
                'error': 'Report generation failed',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Echo:
    """An object that implements just the write method of the file-like interface."""
    def write(self, value):
        return value

class ReportExportCSVView(APIView):
    """
    GET: Generate and download a CSV export of the carbon entries (Audit Trail).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        user = request.user
        if not user.cabinet:
            raise PermissionDenied('No cabinet')
            
        report = get_object_or_404(Report, id=pk, cabinet=user.cabinet)
        
        if report.status != 'completed':
            return Response({'error': 'Report not completed'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Log download
        ReportAuditTrail.objects.create(
            report=report,
            user=user,
            action='csv_export_downloaded',
            ip_address=request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        )
        
        def iter_items():
            # Header with UTF-8 BOM
            yield ['\ufeffLigne FEC', 'Date', 'Compte', 'Libellé', 'Débit', 'Crédit', 'Facteur Emission', 'CO2e (kg)', 'DQR']
            
            # Use iterator() to stream results without loading all in RAM
            entries = CarbonEntry.objects.filter(report=report).select_related('emission_factor').iterator(chunk_size=2000)
            
            for entry in entries:
                yield [
                    str(entry.fec_line_number) if entry.fec_line_number is not None else '',
                    entry.ecriture_date.strftime('%Y-%m-%d') if entry.ecriture_date else '',
                    entry.compte_num or '',
                    entry.compte_lib or '',
                    f"{entry.debit:.2f}" if entry.debit is not None else '0.00',
                    f"{entry.credit:.2f}" if entry.credit is not None else '0.00',
                    entry.emission_factor.name if entry.emission_factor else '',
                    f"{entry.co2_kg:.2f}" if entry.co2_kg is not None else '0.00',
                    str(entry.dqr) if entry.dqr is not None else ''
                ]

        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in iter_items()),
            content_type="text/csv; charset=utf-8"
        )
        safe_name = slugify(report.client_name) if report.client_name else "client"
        filename = f"piste_audit_{safe_name}_{report.fiscal_year}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response


class EmissionFactorPhysicalListView(generics.ListAPIView):
    """
    GET: List all emission factors that support physical units
    """
    serializer_class = EmissionFactorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return EmissionFactor.objects.filter(value_kg_co2_per_unit__isnull=False)

def compute_matrix_scores(answers_data):
    """
    Calcule les scores Impact et Financier (sur une échelle de 1 à 4)
    et flag les enjeux matériels (seuil à 2.5).
    """
    matrix = []
    
    # Environnement (E)
    # E1_1, E2_1 -> Impact, E3_1 -> Financier
    e1 = answers_data.get('E1_1')
    e2 = answers_data.get('E2_1')
    e3 = answers_data.get('E3_1')
    
    def safe_int(val, default=1):
        try:
            return int(val)
        except (ValueError, TypeError):
            return default
    
    e_impact = 0
    e_impact_count = 0
    if e1 is not None:
        e_impact += safe_int(e1)
        e_impact_count += 1
    if e2 is not None:
        e_impact += safe_int(e2)
        e_impact_count += 1
    e_impact_score = (e_impact / e_impact_count) if e_impact_count > 0 else 1.0
    e_financial_score = safe_int(e3) if e3 is not None else 1.0
    
    matrix.append({
        'topic': 'Environnement',
        'impact': round(e_impact_score, 2),
        'financial': float(e_financial_score),
        'is_material': e_impact_score >= 2.5 or e_financial_score >= 2.5
    })
    
    # Social (S)
    # S1_1 -> Impact, S2_1 (bool) -> Financier (True=1, False=4)
    s1 = answers_data.get('S1_1')
    s2 = answers_data.get('S2_1')
    
    s_impact_score = safe_int(s1) if s1 is not None else 1.0
    s_financial_score = 1.0 if s2 is True else (4.0 if s2 is False else 1.0)
    
    matrix.append({
        'topic': 'Social',
        'impact': float(s_impact_score),
        'financial': s_financial_score,
        'is_material': s_impact_score >= 2.5 or s_financial_score >= 2.5
    })
    
    # Gouvernance (G)
    # G2_1 -> Impact, G1_1 (bool) -> Financier (True=1, False=4)
    g2 = answers_data.get('G2_1')
    g1 = answers_data.get('G1_1')
    
    g_impact_score = safe_int(g2) if g2 is not None else 1.0
    g_financial_score = 1.0 if g1 is True else (4.0 if g1 is False else 1.0)
    
    matrix.append({
        'topic': 'Gouvernance',
        'impact': float(g_impact_score),
        'financial': g_financial_score,
        'is_material': g_impact_score >= 2.5 or g_financial_score >= 2.5
    })
    
    return matrix


class MaterialityAssessmentDetailView(generics.GenericAPIView):
    """
    GET, POST, PATCH: Manage double materiality assessment for a report.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MaterialityAssessmentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.cabinet:
            return Report.objects.filter(cabinet=user.cabinet)
        return Report.objects.none()

    def get_object(self):
        report = get_object_or_404(self.get_queryset(), id=self.kwargs['pk'])
        try:
            return report.materiality_assessment
        except ObjectDoesNotExist:
            raise Http404

    def get(self, request, pk):
        try:
            assessment = self.get_object()
        except Http404:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = self.get_serializer(assessment)
        return Response(serializer.data)
        
    def post(self, request, pk):
        report = get_object_or_404(self.get_queryset(), id=pk)
        
        if MaterialityAssessment.objects.filter(report=report).exists():
            return Response({'error': 'Assessment already exists, use PATCH.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if isinstance(request.data, dict):
            request_data = request.data.copy()
        elif hasattr(request.data, 'dict'):
            request_data = request.data.dict()
        else:
            return Response({'error': 'Invalid data format.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if 'data' in request_data and isinstance(request_data['data'], dict):
            answers = request_data['data'].copy()
            answers.pop('computed_matrix', None)
            request_data['data']['computed_matrix'] = compute_matrix_scores(answers)
            
        serializer = self.get_serializer(data=request_data)
        if serializer.is_valid():
            try:
                serializer.save(report=report)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'error': 'Assessment already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def patch(self, request, pk):
        try:
            assessment = self.get_object()
        except Http404:
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if isinstance(request.data, dict):
            request_data = request.data.copy()
        elif hasattr(request.data, 'dict'):
            request_data = request.data.dict()
        else:
            return Response({'error': 'Invalid data format.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if 'data' in request_data and isinstance(request_data['data'], dict):
            existing_data = assessment.data if isinstance(assessment.data, dict) else {}
            merged_answers = existing_data.copy()
            merged_answers.update(request_data['data'])
            merged_answers.pop('computed_matrix', None)
            
            request_data['data']['computed_matrix'] = compute_matrix_scores(merged_answers)
            
        serializer = self.get_serializer(assessment, data=request_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportIXBRLView(APIView):
    """
    POST: Trigger iXBRL generation and validation task.
    GET: Download the validated iXBRL file.
    """
    permission_classes = [permissions.IsAuthenticated]

    def _get_report(self, pk):
        user = self.request.user
        if not user.cabinet:
            raise PermissionDenied("User must belong to a cabinet")
        
        return get_object_or_404(Report, id=pk, cabinet=user.cabinet)

    def post(self, request, pk):
        from .tasks import generate_ixbrl_task
        
        report = self._get_report(pk)
        
        if report.status == 'processing':
            return Response(
                {"error": "Une génération est déjà en cours"},
                status=status.HTTP_409_CONFLICT
            )
            
        if report.status not in ['completed', 'failed']:
            return Response(
                {"error": "Le rapport doit être au statut 'completed' ou 'failed' pour générer l'iXBRL."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if report.has_pending_physical_data:
            return Response(
                {"error": "Saisie physique incomplète. Vous devez compléter les quantités physiques avant de générer l'iXBRL."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Check and deduct credit
        from apps.credits.services import CreditService
        credit_service = CreditService()
        success, error_msg = credit_service.deduct_credit_for_report(report, user=self.request.user)
        if not success:
            return Response({
                'error': 'Insufficient credits',
                'detail': error_msg
            }, status=status.HTTP_402_PAYMENT_REQUIRED)
            
        from apps.core.models import USE_TENANTS
        
        schema_name = report.cabinet.schema_name if USE_TENANTS else None
        generate_ixbrl_task.delay(report.id, schema_name)
        
        ReportAuditTrail.objects.create(
            report=report,
            user=self.request.user,
            action='ixbrl_generated',
            details={'ip_address': request.META.get('REMOTE_ADDR')}
        )
        
        return Response(
            {"message": "Génération et validation iXBRL lancées en arrière-plan."},
            status=status.HTTP_202_ACCEPTED
        )

    def get(self, request, pk):
        from django.core.files.storage import default_storage
        
        report = self._get_report(pk)
        
        if not report.ixbrl_url or not default_storage.exists(report.ixbrl_url):
            return Response(
                {"error": "Fichier iXBRL non disponible ou en cours de génération."},
                status=status.HTTP_404_NOT_FOUND
            )
            
        ReportAuditTrail.objects.create(
            report=report,
            user=self.request.user,
            action='ixbrl_downloaded',
            details={'ip_address': request.META.get('REMOTE_ADDR')}
        )
        
        filename = f"esef-report-{report.client_name}-{report.fiscal_year}.html"
        return FileResponse(
            default_storage.open(report.ixbrl_url, 'rb'), 
            as_attachment=True, 
            filename=filename, 
            content_type='application/xhtml+xml'
        )
