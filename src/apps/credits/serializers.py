"""
Credits serializers
"""
from rest_framework import serializers
from .models import CreditPack, CreditTransaction
from apps.core.models import CreditBalance


class CreditPackSerializer(serializers.ModelSerializer):
    """Serializer for credit packs."""
    price_per_credit = serializers.ReadOnlyField()
    
    class Meta:
        model = CreditPack
        fields = ['id', 'name', 'credits', 'price_euros', 'price_per_credit', 'description']


class CreditBalanceSerializer(serializers.Serializer):
    """Serializer for credit balance."""
    balance = serializers.IntegerField()
    last_purchase_at = serializers.DateTimeField(allow_null=True)
    alert_threshold = serializers.IntegerField()
    is_low = serializers.BooleanField()


class CreditTransactionSerializer(serializers.ModelSerializer):
    """Serializer for credit transactions."""
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CreditTransaction
        fields = [
            'id', 'transaction_type', 'credits', 'balance_after',
            'amount_euros', 'user_name', 'status', 'created_at'
        ]
        read_only_fields = fields
    
    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return None


class PurchaseCreditsSerializer(serializers.Serializer):
    """Serializer for purchasing credits."""
    credit_pack_id = serializers.IntegerField()
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()


class AllocateCreditsSerializer(serializers.Serializer):
    """Serializer for allocating credits to a user."""
    user_id = serializers.IntegerField()
    credits = serializers.IntegerField(min_value=0)
