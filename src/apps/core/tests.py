"""
Tests for core app models.
"""
import pytest
from django.contrib.auth import get_user_model
from apps.core.models import Cabinet, CreditBalance


User = get_user_model()


@pytest.mark.django_db
class TestCabinetModel:
    """Tests for Cabinet model."""

    def test_create_cabinet(self):
        """Test creating a cabinet."""
        cabinet = Cabinet.objects.create(
            schema_name='test_cabinet',
            name='Cabinet Test',
            siret='12345678901234',
            plan='starter',
        )
        assert cabinet.name == 'Cabinet Test'
        assert cabinet.siret == '12345678901234'
        assert cabinet.plan == 'starter'
        assert str(cabinet) == 'Cabinet Test'

    def test_cabinet_default_values(self):
        """Test cabinet default values."""
        cabinet = Cabinet.objects.create(
            schema_name='test2',
            name='Test 2',
        )
        assert cabinet.plan == 'starter'
        assert cabinet.credit_alert_threshold == 5


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model."""

    def test_create_user(self):
        """Test creating a user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert user.role == 'collaborator'

    def test_user_credits(self):
        """Test user credit properties."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            credits_allocated=10,
            credits_used=3,
        )
        assert user.credits_remaining == 7

    def test_user_is_admin(self):
        """Test is_cabinet_admin property."""
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass',
            role='admin',
        )
        collab = User.objects.create_user(
            username='collab',
            email='collab@example.com',
            password='collabpass',
            role='collaborator',
        )
        assert admin.is_cabinet_admin is True
        assert collab.is_cabinet_admin is False


@pytest.mark.django_db
class TestCreditBalanceModel:
    """Tests for CreditBalance model."""

    def test_credit_balance_str(self):
        """Test CreditBalance string representation."""
        cabinet = Cabinet.objects.create(
            schema_name='test',
            name='Test Cabinet',
        )
        balance = CreditBalance.objects.create(
            cabinet=cabinet,
            balance=50,
        )
        assert str(balance) == 'Test Cabinet: 50 crédits'


def test_celery_ping_task():
    """Test the celery ping task."""
    from ledgercarbon.celery import ping
    result = ping.delay()
    assert result.get() == 'pong'
