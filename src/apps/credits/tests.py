from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
import stripe

from apps.core.models import Cabinet, User, CreditBalance
from apps.credits.models import CreditPack, CreditTransaction


class StripeIntegrationTests(TestCase):
    def setUp(self):
        self.cabinet = Cabinet.objects.create(name="Test Cabinet", schema_name="test_schema")
        self.client = APIClient()
        
        # Create users
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password="password123",
            cabinet=self.cabinet,
            role="admin"
        )
        self.collab_user = User.objects.create_user(
            username="collab_user",
            password="password123",
            cabinet=self.cabinet,
            role="collaborator"
        )
        
        # Initialize credit balance
        CreditBalance.objects.create(cabinet=self.cabinet, balance=10)
        
        # Create credit pack
        self.credit_pack = CreditPack.objects.create(
            name="Pack 10",
            credits=10,
            price_euros=150.00,
            is_active=True
        )

    def test_purchase_requires_auth(self):
        url = reverse('credit_purchase')
        data = {
            'credit_pack_id': self.credit_pack.id,
            'success_url': 'http://testserver.com/success',
            'cancel_url': 'http://testserver.com/cancel'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_collaborator_cannot_purchase(self):
        self.client.force_authenticate(user=self.collab_user)
        url = reverse('credit_purchase')
        data = {
            'credit_pack_id': self.credit_pack.id,
            'success_url': 'http://testserver.com/success',
            'cancel_url': 'http://testserver.com/cancel'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['error'], 'Only cabinet admins can purchase credits')

    @patch('stripe.checkout.Session.create')
    @patch('stripe.Customer.create')
    def test_admin_can_purchase(self, mock_customer_create, mock_session_create):
        # Configure the mock returns
        mock_customer_create.return_value = MagicMock(id='cus_test123')
        mock_session_create.return_value = MagicMock(url='https://checkout.stripe.com/test')

        self.client.force_authenticate(user=self.admin_user)
        url = reverse('credit_purchase')
        data = {
            'credit_pack_id': self.credit_pack.id,
            'success_url': 'http://testserver.com/success',
            'cancel_url': 'http://testserver.com/cancel'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['checkout_url'], 'https://checkout.stripe.com/test')
        
        # Verify Stripe calls
        mock_customer_create.assert_called_once()
        mock_session_create.assert_called_once()
        
        # Verify cabinet was updated with customer ID
        self.cabinet.refresh_from_db()
        self.assertEqual(self.cabinet.stripe_customer_id, 'cus_test123')

    def test_webhook_invalid_signature(self):
        url = reverse('stripe_webhook')
        # Missing or invalid signature should raise an error and return 400
        response = self.client.post(url, data="invalid_payload", content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('stripe.Webhook.construct_event')
    @patch('stripe.checkout.Session.retrieve')
    def test_webhook_checkout_completed(self, mock_session_retrieve, mock_construct_event):
        # Mock the webhook event construction
        mock_construct_event.return_value = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_123',
                }
            }
        }
        
        # Mock the session retrieval that the service performs
        mock_session_retrieve.return_value = MagicMock(
            payment_status='paid',
            metadata={
                'cabinet_id': str(self.cabinet.id),
                'credit_pack_id': str(self.credit_pack.id),
                'credits': str(self.credit_pack.credits),
            },
            payment_intent='pi_test_123'
        )

        initial_balance = self.cabinet.credit_balance.balance
        
        url = reverse('stripe_webhook')
        # Simulate webhook post
        response = self.client.post(
            url, 
            data='{"type": "checkout.session.completed"}', 
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE='t=123,v1=fake_signature'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the credits were added
        self.cabinet.credit_balance.refresh_from_db()
        self.assertEqual(self.cabinet.credit_balance.balance, initial_balance + self.credit_pack.credits)
        
        # Verify transaction was created
        self.assertTrue(CreditTransaction.objects.filter(
            cabinet=self.cabinet, 
            transaction_type='purchase',
            stripe_payment_intent_id='pi_test_123'
        ).exists())

    @patch('stripe.Webhook.construct_event')
    @patch('stripe.checkout.Session.retrieve')
    def test_webhook_checkout_unpaid(self, mock_session_retrieve, mock_construct_event):
        # Mock an unpaid session
        mock_construct_event.return_value = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'cs_test_123',
                }
            }
        }
        mock_session_retrieve.return_value = MagicMock(
            payment_status='unpaid'
        )

        initial_balance = self.cabinet.credit_balance.balance
        
        url = reverse('stripe_webhook')
        response = self.client.post(
            url, 
            data='{"type": "checkout.session.completed"}', 
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE='t=123,v1=fake_signature'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify NO credits were added
        self.cabinet.credit_balance.refresh_from_db()
        self.assertEqual(self.cabinet.credit_balance.balance, initial_balance)

class CreditDeductionTests(TestCase):
    def setUp(self):
        self.cabinet = Cabinet.objects.create(name="Test Cabinet 2", schema_name="test_schema_2")
        self.user = User.objects.create_user(username="test_user_2", password="password", cabinet=self.cabinet)
        from apps.report_generator.models import Report
        self.report = Report.objects.create(cabinet=self.cabinet, created_by=self.user, client_name="Test", fiscal_year=2023, status='completed')
        from apps.credits.services import CreditService
        self.credit_service = CreditService()
        
    def test_deduction_on_first_export(self):
        # Setup balance
        CreditBalance.objects.create(cabinet=self.cabinet, balance=5)
        
        # Act
        success, error = self.credit_service.deduct_credit_for_report(self.report, self.user)
        
        # Assert
        self.assertTrue(success)
        self.report.refresh_from_db()
        self.assertTrue(self.report.is_unlocked)
        self.cabinet.credit_balance.refresh_from_db()
        self.assertEqual(self.cabinet.credit_balance.balance, 4)
        
        # Verify transaction
        self.assertTrue(CreditTransaction.objects.filter(
            report=self.report, transaction_type='consumption', credits=-1
        ).exists())

    def test_no_deduction_on_subsequent_export(self):
        # Setup balance
        CreditBalance.objects.create(cabinet=self.cabinet, balance=5)
        self.report.is_unlocked = True
        self.report.save()
        
        # Act
        success, error = self.credit_service.deduct_credit_for_report(self.report, self.user)
        
        # Assert
        self.assertTrue(success)
        self.cabinet.credit_balance.refresh_from_db()
        self.assertEqual(self.cabinet.credit_balance.balance, 5) # Balance unchanged
        self.assertFalse(CreditTransaction.objects.filter(report=self.report).exists())

    def test_deduction_fails_if_insufficient_credits(self):
        # Setup balance = 0
        CreditBalance.objects.create(cabinet=self.cabinet, balance=0)
        
        # Act
        success, error = self.credit_service.deduct_credit_for_report(self.report, self.user)
        
        # Assert
        self.assertFalse(success)
        self.assertEqual(error, "Solde de crédits insuffisant")
        self.report.refresh_from_db()
        self.assertFalse(self.report.is_unlocked)

    def test_deduction_fails_if_cannot_consume_credits(self):
        from django.core.exceptions import PermissionDenied
        # Setup balance = 5
        CreditBalance.objects.create(cabinet=self.cabinet, balance=5)
        self.user.can_consume_credits = False
        self.user.save()
        
        # Act & Assert
        success, msg = self.credit_service.deduct_credit_for_report(self.report, self.user)
        self.assertFalse(success)
        self.assertEqual(msg, "Vous n'avez pas l'autorisation de consommer des crédits.")
            
        self.report.refresh_from_db()
        self.assertFalse(self.report.is_unlocked)

    @patch('apps.credits.tasks.send_low_credit_alert_task.delay')
    def test_deduction_triggers_low_credit_alert(self, mock_delay):
        # Setup balance to threshold + 1
        self.cabinet.credit_alert_threshold = 5
        self.cabinet.save()
        CreditBalance.objects.create(cabinet=self.cabinet, balance=6)
        
        # Act
        with self.captureOnCommitCallbacks(execute=True):
            success, error = self.credit_service.deduct_credit_for_report(self.report, self.user)
            
        self.assertTrue(success)
        mock_delay.assert_called_once_with(self.cabinet.id, 5)

    @patch('apps.credits.tasks.send_low_credit_alert_task.delay')
    def test_deduction_does_not_trigger_low_credit_alert_if_already_below_threshold(self, mock_delay):
        # Setup balance to threshold
        self.cabinet.credit_alert_threshold = 5
        self.cabinet.save()
        CreditBalance.objects.create(cabinet=self.cabinet, balance=5)
        
        # Act
        with self.captureOnCommitCallbacks(execute=True):
            success, error = self.credit_service.deduct_credit_for_report(self.report, self.user)
            
        self.assertTrue(success)
        mock_delay.assert_not_called()
