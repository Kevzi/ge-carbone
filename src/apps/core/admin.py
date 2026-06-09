"""
Core admin
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Cabinet, Domain, User, CreditBalance, AuditLog


from django_tenants.admin import TenantAdminMixin

@admin.register(Cabinet)
class CabinetAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'siret', 'plan', 'created_at']
    list_filter = ['plan']
    search_fields = ['name', 'siret']


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'cabinet', 'role', 'credits_allocated']
    list_filter = ['role', 'cabinet']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Cabinet & Crédits', {'fields': ('cabinet', 'role', 'credits_allocated', 'credits_used')}),
    )


@admin.register(CreditBalance)
class CreditBalanceAdmin(admin.ModelAdmin):
    list_display = ['cabinet', 'balance', 'last_purchase_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'created_at', 'ip_address']
    list_filter = ['action', 'created_at']
    readonly_fields = ['cabinet', 'user', 'action', 'details', 'ip_address', 'user_agent', 'created_at']
