"""
Core serializers
"""
from rest_framework import serializers
from .models import User, Cabinet, CreditBalance


class CabinetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cabinet
        fields = ['id', 'name', 'siret', 'plan', 'created_at']
        read_only_fields = ['id', 'created_at']


class CreditBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditBalance
        fields = ['balance', 'last_purchase_at']
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    cabinet = CabinetSerializer(read_only=True)
    credits_remaining = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'cabinet', 'role', 'credits_allocated', 'credits_used',
            'credits_remaining', 'is_cabinet_admin', 'can_consume_credits',
            'is_superuser'
        ]
        read_only_fields = ['id', 'credits_used', 'credits_remaining', 'is_cabinet_admin', 'is_superuser']
