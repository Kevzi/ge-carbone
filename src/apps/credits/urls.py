"""
Credits URLs
"""
from django.urls import path
from .views import (
    CreditPackListView,
    CreditBalanceView,
    CreditPurchaseView,
    CreditTransactionListView,
    AllocateCreditsView,
    StripeWebhookView,
)

urlpatterns = [
    path('packs/', CreditPackListView.as_view(), name='credit_packs'),
    path('balance/', CreditBalanceView.as_view(), name='credit_balance'),
    path('purchase/', CreditPurchaseView.as_view(), name='credit_purchase'),
    path('transactions/', CreditTransactionListView.as_view(), name='credit_transactions'),
    path('allocate/', AllocateCreditsView.as_view(), name='credit_allocate'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),
]
