from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.db.models import Sum, Count, F
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination

from .models import Cabinet, User, CreditBalance, AuditLog
from apps.report_generator.models import Report

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000

class StatsViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    def list(self, request):
        total_cabinets = Cabinet.objects.count()
        total_users = User.objects.count()
        
        # Credits Usage
        credits_aggr = CreditBalance.objects.aggregate(total_balance=Sum('balance'))
        total_balance = credits_aggr['total_balance'] or 0
        
        # Reports / Celery Health
        completed_reports = Report.objects.filter(status='completed').count()
        failed_reports = Report.objects.filter(status='failed').count()
        total_processed = completed_reports + failed_reports
        
        success_rate = 100
        if total_processed > 0:
            success_rate = round((completed_reports / total_processed) * 100, 1)
            
        total_reports_generated = Report.objects.count()

        return Response({
            "total_cabinets": total_cabinets,
            "total_users": total_users,
            "credits_total_balance": total_balance,
            "celery_health": {
                "success_rate": success_rate,
                "completed_count": completed_reports,
                "failed_count": failed_reports,
            },
            "usage": {
                "total_reports": total_reports_generated,
            }
        })


class GlobalCabinetViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Cabinet.objects.all().annotate(
            user_count=Count('users', distinct=True)
        ).select_related('credit_balance')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        cabinet_list = page if page is not None else queryset
        
        data = []
        for cabinet in cabinet_list:
            data.append({
                "id": cabinet.id,
                "name": cabinet.name,
                "plan": cabinet.plan,
                "user_count": cabinet.user_count,
                "credits_balance": cabinet.credit_balance.balance if hasattr(cabinet, 'credit_balance') else 0,
                "created_at": cabinet.created_at
            })
            
        if page is not None:
            return self.get_paginated_response(data)
        return Response(data)

    @action(detail=True, methods=['post'])
    def add_credits(self, request, pk=None):
        cabinet = self.get_object()
        try:
            amount = int(request.data.get('amount', 0))
        except (ValueError, TypeError):
            return Response({"error": "Invalid amount format"}, status=status.HTTP_400_BAD_REQUEST)
            
        if amount <= 0 or amount > 1000000:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
            
        cb, _ = CreditBalance.objects.get_or_create(cabinet=cabinet)
        cb.balance = F('balance') + amount
        cb.save(update_fields=['balance'])
        cb.refresh_from_db()
        
        AuditLog.objects.create(
            cabinet=cabinet,
            user=request.user,
            action='credits_allocated',
            details={"added": amount, "new_balance": cb.balance, "note": "Super Admin manual allocation"}
        )
        
        return Response({"message": f"{amount} credits added", "new_balance": cb.balance})


class ImpersonationView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            user_id = int(request.data.get('user_id'))
        except (ValueError, TypeError):
            return Response({"error": "Invalid user_id format"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            target_user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return Response({"error": "Active User not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # Log the impersonation action
        AuditLog.objects.create(
            cabinet=target_user.cabinet if target_user.cabinet else None,
            user=request.user,
            action='impersonate',
            details={"target_user_id": target_user.id, "target_username": target_user.username, "cabinet": target_user.cabinet.name if target_user.cabinet else "None"}
        )
            
        refresh = RefreshToken.for_user(target_user)
        # Inject tenant_id claim
        if target_user.cabinet and hasattr(target_user.cabinet, 'schema_name'):
            refresh['tenant_id'] = target_user.cabinet.schema_name
        elif hasattr(target_user, 'tenant_id'):
            refresh['tenant_id'] = target_user.tenant_id
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'impersonated_user': target_user.username
        })

class GlobalUserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination
    queryset = User.objects.all().select_related('cabinet')
    
    def list(self, request, *args, **kwargs):
        cabinet_id = request.query_params.get('cabinet_id')
        queryset = self.filter_queryset(self.get_queryset())
        if cabinet_id:
            queryset = queryset.filter(cabinet_id=cabinet_id)
            
        page = self.paginate_queryset(queryset)
        user_list = page if page is not None else queryset
        
        data = []
        for user in user_list:
            data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "cabinet_name": user.cabinet.name if user.cabinet else None,
                "role": user.role,
                "is_superuser": user.is_superuser
            })
            
        if page is not None:
            return self.get_paginated_response(data)
        return Response(data)
