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
        total_cabinets = Cabinet.objects.exclude(schema_name='public').count()
        total_users = User.objects.count()
        
        # Credits Usage
        credits_aggr = CreditBalance.objects.aggregate(total_balance=Sum('balance'))
        total_balance = credits_aggr['total_balance'] or 0
        
        from apps.report_generator.models import Report
        from django_tenants.utils import tenant_context
        
        total_reports = 0
        completed_reports = 0
        failed_reports = 0
        
        from django.db import transaction
        
        for tenant in Cabinet.objects.exclude(schema_name='public'):
            try:
                with transaction.atomic():
                    with tenant_context(tenant):
                        completed_reports += Report.objects.filter(status='completed').count()
                        failed_reports += Report.objects.filter(status='failed').count()
                        total_reports += Report.objects.count()
            except Exception:
                pass
        
        total_processed = completed_reports + failed_reports
        success_rate = 0
        
        if total_processed > 0:
            success_rate = round((completed_reports / total_processed) * 100, 1)
            
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
                "total_reports": total_reports,
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

    @action(detail=False, methods=['post'])
    def create_cabinet(self, request):
        name = request.data.get('name')
        if not name:
            return Response({"error": "Le nom du cabinet est requis."}, status=400)
            
        import re
        from apps.core.models import Cabinet, Domain, User, CreditBalance
        from django.contrib.auth.hashers import make_password
        
        schema_name = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
        if not schema_name:
            schema_name = "cabinet"
            
        base_schema_name = schema_name
        counter = 1
        while Cabinet.objects.filter(schema_name=schema_name).exists():
            schema_name = f"{base_schema_name}{counter}"
            counter += 1
            
        try:
            cabinet = Cabinet(schema_name=schema_name, name=name, plan='enterprise')
            cabinet.save()
            
            domain = Domain(domain=f"{schema_name}.localhost", tenant=cabinet, is_primary=True)
            domain.save()
            
            CreditBalance.objects.create(cabinet=cabinet, balance=100)
            
            admin_username = f"admin_{schema_name}"
            user = User.objects.create(
                username=admin_username,
                email=f"{admin_username}@example.com",
                password=make_password("password"),
                cabinet=cabinet,
                role="admin"
            )
            
            return Response({
                "id": cabinet.id, 
                "name": cabinet.name, 
                "admin_username": user.username
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)

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

    @action(detail=True, methods=['delete'])
    def delete_cabinet(self, request, pk=None):
        cabinet = self.get_object()
        
        # Don't allow deleting the public schema
        if cabinet.schema_name == 'public':
            return Response({"error": "Cannot delete public schema"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # We use force_drop=True to drop the PostgreSQL schema
            cabinet.delete(force_drop=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            # Fallback to raw SQL if django-tenants fails (e.g. broken schema)
            try:
                from django.db import connection, transaction
                with transaction.atomic():
                    with connection.cursor() as cursor:
                        s = cabinet.schema_name
                        cursor.execute(f"DELETE FROM core_domain WHERE tenant_id IN (SELECT id FROM core_cabinet WHERE schema_name = '{s}');")
                        cursor.execute(f"DELETE FROM core_user WHERE cabinet_id IN (SELECT id FROM core_cabinet WHERE schema_name = '{s}');")
                        cursor.execute(f"DELETE FROM core_creditbalance WHERE cabinet_id IN (SELECT id FROM core_cabinet WHERE schema_name = '{s}');")
                        cursor.execute(f"DELETE FROM core_cabinet WHERE schema_name = '{s}';")
                        cursor.execute(f"DROP SCHEMA IF EXISTS {s} CASCADE;")
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e2:
                return Response({"error": f"Error deleting cabinet: {str(e)} / {str(e2)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



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
