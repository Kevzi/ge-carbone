"""
Credits services - Stripe integration and credit management.
"""
import stripe
import logging
from decimal import Decimal
from typing import Optional, Tuple
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import CreditPack, CreditTransaction
from apps.core.models import Cabinet, CreditBalance, User

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


class StripeService:
    """
    Service for Stripe payment integration.
    """
    
    def create_checkout_session(
        self,
        cabinet: Cabinet,
        credit_pack: CreditPack,
        success_url: str,
        cancel_url: str
    ) -> Optional[str]:
        """
        Create a Stripe Checkout session for credit purchase.
        
        Returns:
            Checkout session URL or None on error
        """
        try:
            # Get or create Stripe customer
            if not cabinet.stripe_customer_id:
                customer = stripe.Customer.create(
                    name=cabinet.name,
                    metadata={'cabinet_id': cabinet.id}
                )
                cabinet.stripe_customer_id = customer.id
                cabinet.save()
            
            # Create checkout session
            session = stripe.checkout.Session.create(
                customer=cabinet.stripe_customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'unit_amount': int(credit_pack.price_euros * 100),  # Cents
                        'product_data': {
                            'name': f'LedgerCarbon - {credit_pack.name}',
                            'description': f'{credit_pack.credits} crédits pour rapports carbone',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'cabinet_id': str(cabinet.id),
                    'credit_pack_id': str(credit_pack.id),
                    'credits': str(credit_pack.credits),
                }
            )
            
            return session.url
            
        except stripe.error.StripeError as e:
            logger.exception(f"Stripe error creating checkout: {e}")
            return None
    
    def handle_payment_success(self, session_id: str) -> bool:
        """
        Handle successful payment webhook.
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status != 'paid':
                return False
            
            cabinet_id = int(session.metadata.get('cabinet_id'))
            credits = int(session.metadata.get('credits'))
            credit_pack_id = int(session.metadata.get('credit_pack_id'))
            
            cabinet = Cabinet.objects.get(id=cabinet_id)
            credit_pack = CreditPack.objects.get(id=credit_pack_id)
            
            # Add credits
            credit_service = CreditService()
            credit_service.add_credits(
                cabinet=cabinet,
                credits=credits,
                credit_pack=credit_pack,
                stripe_payment_intent_id=session.payment_intent,
                amount_euros=credit_pack.price_euros
            )
            
            return True
            
        except Exception as e:
            logger.exception(f"Error handling payment success: {e}")
            return False


class CreditService:
    """
    Service for credit management.
    """
    
    def get_balance(self, cabinet: Cabinet) -> int:
        """Get current credit balance for a cabinet."""
        balance, _ = CreditBalance.objects.get_or_create(
            cabinet=cabinet,
            defaults={'balance': 0}
        )
        return balance.balance
    
    @transaction.atomic
    def add_credits(
        self,
        cabinet: Cabinet,
        credits: int,
        credit_pack: Optional[CreditPack] = None,
        user: Optional[User] = None,
        stripe_payment_intent_id: str = '',
        amount_euros: Optional[Decimal] = None,
        notes: str = ''
    ) -> CreditTransaction:
        """
        Add credits to a cabinet's balance.
        """
        balance, _ = CreditBalance.objects.get_or_create(
            cabinet=cabinet,
            defaults={'balance': 0}
        )
        
        balance_before = balance.balance
        balance.balance += credits
        balance.last_purchase_at = timezone.now()
        balance.save()
        
        transaction = CreditTransaction.objects.create(
            cabinet=cabinet,
            user=user,
            transaction_type='purchase',
            credits=credits,
            balance_before=balance_before,
            balance_after=balance.balance,
            credit_pack=credit_pack,
            amount_euros=amount_euros,
            stripe_payment_intent_id=stripe_payment_intent_id,
            status='completed',
            notes=notes
        )
        
        logger.info(
            f"Added {credits} credits to cabinet {cabinet.name}. "
            f"New balance: {balance.balance}"
        )
        
        return transaction
    
    @transaction.atomic
    def consume_credit(
        self,
        cabinet: Cabinet,
        user: Optional[User] = None,
        report_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Consume one credit for a report.
        
        Returns:
            Tuple of (success, error_message)
        """
        balance, _ = CreditBalance.objects.get_or_create(
            cabinet=cabinet,
            defaults={'balance': 0}
        )
        
        if balance.balance <= 0:
            return False, "Solde de crédits insuffisant"
        
        balance_before = balance.balance
        balance.balance -= 1
        balance.save()
        
        # Update user's usage if provided
        if user:
            user.credits_used += 1
            user.save()
        
        # Create transaction record
        from apps.report_generator.models import Report
        report = None
        if report_id:
            try:
                report = Report.objects.get(id=report_id)
            except Report.DoesNotExist:
                pass
        
        CreditTransaction.objects.create(
            cabinet=cabinet,
            user=user,
            transaction_type='consumption',
            credits=-1,
            balance_before=balance_before,
            balance_after=balance.balance,
            report=report,
            status='completed'
        )
        
        logger.info(
            f"Consumed 1 credit from cabinet {cabinet.name}. "
            f"New balance: {balance.balance}"
        )
        
        return True, ""
    
    @transaction.atomic
    def refund_credit(
        self,
        cabinet: Cabinet,
        user: Optional[User] = None,
        report_id: Optional[int] = None,
        reason: str = ''
    ) -> CreditTransaction:
        """
        Refund a credit (e.g., if report processing failed).
        """
        balance, _ = CreditBalance.objects.get_or_create(
            cabinet=cabinet,
            defaults={'balance': 0}
        )
        
        balance_before = balance.balance
        balance.balance += 1
        balance.save()
        
        # Update user's usage if provided
        if user and user.credits_used > 0:
            user.credits_used -= 1
            user.save()
        
        transaction = CreditTransaction.objects.create(
            cabinet=cabinet,
            user=user,
            transaction_type='refund',
            credits=1,
            balance_before=balance_before,
            balance_after=balance.balance,
            status='completed',
            notes=reason
        )
        
        logger.info(
            f"Refunded 1 credit to cabinet {cabinet.name}. "
            f"Reason: {reason}"
        )
        
        return transaction
    
    def allocate_to_user(
        self,
        cabinet: Cabinet,
        user: User,
        credits: int,
        allocated_by: Optional[User] = None
    ) -> bool:
        """
        Allocate credits to a user (quota, not deduction from pool).
        """
        if user.cabinet != cabinet:
            return False
        
        user.credits_allocated = credits
        user.save()
        
        logger.info(
            f"Allocated {credits} credits to user {user.username} "
            f"in cabinet {cabinet.name}"
        )
        
        return True
    
    def check_alert_threshold(self, cabinet: Cabinet) -> bool:
        """
        Check if cabinet balance is below alert threshold.
        """
        balance = self.get_balance(cabinet)
        return balance <= cabinet.credit_alert_threshold
