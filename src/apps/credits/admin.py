"""
Credits admin
"""
from django.contrib import admin
from .models import CreditPack, CreditTransaction


@admin.register(CreditPack)
class CreditPackAdmin(admin.ModelAdmin):
    list_display = ['name', 'credits', 'price_euros', 'is_active']
    list_filter = ['is_active']


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ['cabinet', 'user', 'transaction_type', 'credits', 'balance_after', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['cabinet__name', 'user__username']
    readonly_fields = ['created_at']
    raw_id_fields = ['cabinet', 'user', 'credit_pack', 'report']
