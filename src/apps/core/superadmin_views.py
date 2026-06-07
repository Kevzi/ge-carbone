from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Cabinet, User, CreditBalance, AuditLog
from apps.report_generator.models import Report

class IsSuperAdminUser(permissions.BasePermission):
    """
    Allows access only to superusers.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

class StatsView(APIView):
    permission_classes = [IsSuperAdminUser]

    def get(self, request):
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
    permission_classes = [IsSuperAdminUser]
    queryset = Cabinet.objects.all().annotate(user_count=Count('users'))
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for cabinet in queryset:
            cb, _ = CreditBalance.objects.get_or_create(cabinet=cabinet)
            data.append({
                "id": cabinet.id,
                "name": cabinet.name,
                "plan": cabinet.plan,
                "user_count": cabinet.user_count,
                "credits_balance": cb.balance,
                "created_at": cabinet.created_at
            })
        return Response(data)

    @action(detail=True, methods=['post'])
    def add_credits(self, request, pk=None):
        cabinet = self.get_object()
        amount = int(request.data.get('amount', 0))
        if amount <= 0:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
            
        cb, _ = CreditBalance.objects.get_or_create(cabinet=cabinet)
        cb.balance += amount
        cb.save()
        
        AuditLog.objects.create(
            cabinet=cabinet,
            user=request.user,
            action='credits_allocated',
            details={"added": amount, "new_balance": cb.balance, "note": "Super Admin manual allocation"}
        )
        
        return Response({"message": f"{amount} credits added", "new_balance": cb.balance})


class ImpersonationView(APIView):
    permission_classes = [IsSuperAdminUser]

    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # Log the impersonation action
        if target_user.cabinet:
            AuditLog.objects.create(
                cabinet=target_user.cabinet,
                user=request.user,
                action='impersonate',
                details={"target_user_id": target_user.id, "target_username": target_user.username}
            )
            
        refresh = RefreshToken.for_user(target_user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'impersonated_user': target_user.username
        })

class GlobalUserViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsSuperAdminUser]
    queryset = User.objects.all().select_related('cabinet')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = []
        for user in queryset:
            data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "cabinet_name": user.cabinet.name if user.cabinet else None,
                "role": user.role,
                "is_superuser": user.is_superuser
            })
        return Response(data)
