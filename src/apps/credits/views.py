"""
Credits views - API endpoints for credit management.
"""
import stripe
import json
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CreditPack, CreditTransaction
from .serializers import (
    CreditPackSerializer, CreditBalanceSerializer,
    CreditTransactionSerializer, PurchaseCreditsSerializer,
    AllocateCreditsSerializer
)
from .services import StripeService, CreditService
from apps.core.models import CreditBalance, User

logger = logging.getLogger(__name__)


class CreditPackListView(generics.ListAPIView):
    """
    GET: List available credit packs
    """
    serializer_class = CreditPackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CreditPack.objects.filter(is_active=True)


class CreditBalanceView(APIView):
    """
    GET: Get current credit balance
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        cabinet = user.cabinet
        
        if not cabinet:
            # Return default balance for users without cabinet
            return Response({
                'balance': 0,
                'last_purchase_at': None,
                'alert_threshold': 5,
                'is_low': True
            })
        
        balance_obj, _ = CreditBalance.objects.get_or_create(
            cabinet=cabinet,
            defaults={'balance': 0}
        )
        
        is_low = balance_obj.balance <= getattr(cabinet, 'credit_alert_threshold', 5)
        
        return Response({
            'balance': balance_obj.balance,
            'last_purchase_at': balance_obj.last_purchase_at,
            'alert_threshold': getattr(cabinet, 'credit_alert_threshold', 5),
            'is_low': is_low
        })


class CreditPurchaseView(APIView):
    """
    POST: Create a Stripe checkout session to purchase credits
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PurchaseCreditsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        cabinet = user.cabinet
        
        if not cabinet:
            return Response({'error': 'No cabinet'}, status=403)
        
        # Only admins can purchase
        if not user.is_cabinet_admin:
            return Response(
                {'error': 'Only cabinet admins can purchase credits'},
                status=403
            )
        
        try:
            credit_pack = CreditPack.objects.get(
                id=serializer.validated_data['credit_pack_id'],
                is_active=True
            )
        except CreditPack.DoesNotExist:
            return Response(
                {'error': 'Credit pack not found'},
                status=404
            )
        
        stripe_service = StripeService()
        checkout_url = stripe_service.create_checkout_session(
            cabinet=cabinet,
            credit_pack=credit_pack,
            success_url=serializer.validated_data['success_url'],
            cancel_url=serializer.validated_data['cancel_url']
        )
        
        if not checkout_url:
            return Response(
                {'error': 'Failed to create checkout session'},
                status=500
            )
        
        return Response({'checkout_url': checkout_url})


class CreditTransactionListView(generics.ListAPIView):
    """
    GET: List credit transactions for the cabinet
    """
    serializer_class = CreditTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.cabinet:
            return CreditTransaction.objects.filter(
                cabinet=user.cabinet
            ).order_by('-created_at')[:50]
        return CreditTransaction.objects.none()


class AllocateCreditsView(APIView):
    """
    POST: Allocate credits to a user (admin only)
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = AllocateCreditsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        cabinet = user.cabinet
        
        if not cabinet:
            return Response({'error': 'No cabinet'}, status=403)
        
        if not user.is_cabinet_admin:
            return Response(
                {'error': 'Only cabinet admins can allocate credits'},
                status=403
            )
        
        try:
            target_user = User.objects.get(
                id=serializer.validated_data['user_id'],
                cabinet=cabinet
            )
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        
        service = CreditService()
        success = service.allocate_to_user(
            cabinet=cabinet,
            user=target_user,
            credits=serializer.validated_data['credits'],
            allocated_by=user
        )
        
        if success:
            return Response({
                'message': f'Allocated {serializer.validated_data["credits"]} credits to {target_user.username}'
            })
        
        return Response({'error': 'Allocation failed'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    POST: Handle Stripe webhooks
    """
    permission_classes = []  # No auth for webhooks
    authentication_classes = []
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            logger.error("Invalid payload in Stripe webhook")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature in Stripe webhook")
            return HttpResponse(status=400)
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            stripe_service = StripeService()
            success = stripe_service.handle_payment_success(session['id'])
            
            if success:
                logger.info(f"Payment successful for session {session['id']}")
            else:
                logger.error(f"Failed to process payment for session {session['id']}")
        
        return HttpResponse(status=200)
