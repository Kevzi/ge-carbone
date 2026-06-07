"""
Core models: Cabinet (Tenant), Domain, User
Supports both multi-tenant (PostgreSQL) and single-tenant (SQLite) modes.
"""
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Check if we're using multi-tenancy
USE_TENANTS = hasattr(settings, 'TENANT_MODEL')

if USE_TENANTS:
    from django_tenants.models import TenantMixin, DomainMixin
    
    class Cabinet(TenantMixin):
        """Cabinet comptable - Tenant principal (multi-tenant mode)."""
        name = models.CharField(max_length=255, verbose_name="Nom du cabinet")
        siret = models.CharField(max_length=14, blank=True, verbose_name="SIRET")
        
        PLAN_CHOICES = [
            ('starter', 'Starter'),
            ('pro', 'Pro'),
            ('enterprise', 'Enterprise'),
        ]
        plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='starter')
        stripe_customer_id = models.CharField(max_length=255, blank=True)
        credit_alert_threshold = models.IntegerField(default=5)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        auto_create_schema = True

        class Meta:
            verbose_name = "Cabinet"
            verbose_name_plural = "Cabinets"

        def __str__(self):
            return self.name

    class Domain(DomainMixin):
        """Domain model for multi-tenant routing."""
        pass

else:
    # Single-tenant mode (SQLite, no django-tenants)
    class Cabinet(models.Model):
        """Cabinet comptable - Single-tenant mode."""
        name = models.CharField(max_length=255, verbose_name="Nom du cabinet")
        schema_name = models.CharField(max_length=63, unique=True, default='public')
        siret = models.CharField(max_length=14, blank=True, verbose_name="SIRET")
        
        PLAN_CHOICES = [
            ('starter', 'Starter'),
            ('pro', 'Pro'),
            ('enterprise', 'Enterprise'),
        ]
        plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='starter')
        stripe_customer_id = models.CharField(max_length=255, blank=True)
        credit_alert_threshold = models.IntegerField(default=5)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        class Meta:
            verbose_name = "Cabinet"
            verbose_name_plural = "Cabinets"

        def __str__(self):
            return self.name

    class Domain(models.Model):
        """Domain model placeholder for single-tenant mode."""
        domain = models.CharField(max_length=253, unique=True)
        tenant = models.ForeignKey(Cabinet, on_delete=models.CASCADE, related_name='domains')
        is_primary = models.BooleanField(default=True)

        def __str__(self):
            return self.domain


class User(AbstractUser):
    """
    Custom User model linked to a Cabinet.
    """
    cabinet = models.ForeignKey(
        Cabinet,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True,
        verbose_name="Cabinet"
    )
    
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('collaborator', 'Collaborateur'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='collaborator',
        verbose_name="Rôle"
    )
    
    credits_allocated = models.IntegerField(default=0, verbose_name="Crédits alloués")
    credits_used = models.IntegerField(default=0, verbose_name="Crédits consommés")
    can_consume_credits = models.BooleanField(default=True, verbose_name="Peut consommer des crédits")
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        cabinet_name = self.cabinet.name if self.cabinet else "No Cabinet"
        return f"{self.get_full_name() or self.username} ({cabinet_name})"
    
    @property
    def credits_remaining(self):
        return self.credits_allocated - self.credits_used
    
    @property
    def is_cabinet_admin(self):
        return self.role == 'admin'


class CreditBalance(models.Model):
    """Solde de crédits global du cabinet."""
    cabinet = models.OneToOneField(
        Cabinet,
        on_delete=models.CASCADE,
        related_name='credit_balance',
        verbose_name="Cabinet"
    )
    balance = models.IntegerField(default=0, verbose_name="Solde")
    last_purchase_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Solde crédits"
        verbose_name_plural = "Soldes crédits"

    def __str__(self):
        return f"{self.cabinet.name}: {self.balance} crédits"


class AuditLog(models.Model):
    """Log d'audit pour traçabilité des actions."""
    cabinet = models.ForeignKey(
        Cabinet,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    
    ACTION_CHOICES = [
        ('login', 'Connexion'),
        ('logout', 'Déconnexion'),
        ('report_created', 'Rapport créé'),
        ('report_downloaded', 'Rapport téléchargé'),
        ('credits_purchased', 'Crédits achetés'),
        ('credits_allocated', 'Crédits alloués'),
        ('user_created', 'Utilisateur créé'),
        ('user_deleted', 'Utilisateur supprimé'),
        ('impersonate', 'Usurpation d\'identité'),
    ]
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Log d'audit"
        verbose_name_plural = "Logs d'audit"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}"
