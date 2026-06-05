"""
Credits models - Credit transactions and Stripe integration
"""
from django.db import models
from django.conf import settings
from decimal import Decimal


class CreditPack(models.Model):
    """
    Packs de crédits disponibles à l'achat.
    """
    name = models.CharField(max_length=100)
    credits = models.IntegerField(verbose_name="Nombre de crédits")
    price_euros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix (€ HT)"
    )
    
    # Stripe
    stripe_price_id = models.CharField(max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pack crédits"
        verbose_name_plural = "Packs crédits"
        ordering = ['credits']

    def __str__(self):
        return f"{self.name}: {self.credits} crédits - {self.price_euros}€"
    
    @property
    def price_per_credit(self):
        return self.price_euros / self.credits


class CreditTransaction(models.Model):
    """
    Transaction de crédits (achat ou consommation).
    """
    cabinet = models.ForeignKey(
        'core.Cabinet',
        on_delete=models.CASCADE,
        related_name='credit_transactions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='credit_transactions'
    )
    
    TYPE_CHOICES = [
        ('purchase', 'Achat'),
        ('consumption', 'Consommation'),
        ('refund', 'Remboursement'),
        ('adjustment', 'Ajustement'),
    ]
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Amount
    credits = models.IntegerField(verbose_name="Crédits")
    balance_before = models.IntegerField(verbose_name="Solde avant")
    balance_after = models.IntegerField(verbose_name="Solde après")
    
    # Purchase details
    credit_pack = models.ForeignKey(
        CreditPack,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    amount_euros = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Stripe
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_invoice_url = models.URLField(blank=True)
    
    # Consumption details
    report = models.ForeignKey(
        'report_generator.Report',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='credit_transactions'
    )
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transaction crédits"
        verbose_name_plural = "Transactions crédits"
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.credits > 0 else ''
        return f"{self.cabinet}: {sign}{self.credits} ({self.transaction_type})"
