"""
Report Generator models - Report and PDF generation
"""
from django.db import models
from django.conf import settings
from decimal import Decimal


class Report(models.Model):
    """
    Rapport carbone généré à partir d'un FEC.
    """
    # Cabinet relation (via tenant)
    cabinet = models.ForeignKey(
        'core.Cabinet',
        on_delete=models.CASCADE,
        related_name='reports'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name='reports'
    )
    
    # Client info
    client_name = models.CharField(max_length=255, verbose_name="Nom client")
    client_siret = models.CharField(max_length=14, blank=True)
    fiscal_year = models.IntegerField(verbose_name="Année fiscale")
    
    # Processing status
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'Traitement en cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échec'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    progress_percent = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    # Results
    total_co2_kg = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name="Total CO2 (kg)"
    )
    scope1_co2_kg = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0')
    )
    scope2_co2_kg = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0')
    )
    scope3_co2_kg = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0')
    )
    
    # Énergie totale pour norme ESRS E1-5 (en MWh)
    total_energy_mwh = models.DecimalField(
        max_digits=15, 
        decimal_places=4, 
        default=0,
        verbose_name="Consommation énergétique (MWh) - ESRS E1-5"
    )
    
    # Quality score (average DQR)
    average_dqr = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('3.00'),
        verbose_name="Score qualité moyen"
    )
    
    # PDF output
    pdf_url = models.URLField(blank=True, verbose_name="URL PDF")
    pdf_generated_at = models.DateTimeField(null=True, blank=True)
    
    xbrl_validation_passed = models.BooleanField(null=True, blank=True, verbose_name="Validation XBRL ESEF")
    xbrl_validation_errors = models.JSONField(null=True, blank=True, verbose_name="Erreurs XBRL")

    # iXBRL export
    ixbrl_url = models.URLField(blank=True, verbose_name="URL iXBRL")
    ixbrl_generated_at = models.DateTimeField(null=True, blank=True)
    
    # Billing & Access
    is_unlocked = models.BooleanField(
        default=False, 
        verbose_name="Débloqué (Crédit consommé)"
    )
    

    # Metadata
    emission_factors_version = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Version facteurs ADEME"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Rapport"
        verbose_name_plural = "Rapports"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client_name} - {self.fiscal_year} ({self.status})"
    
    @property
    def total_co2_tonnes(self):
        """Total en tonnes CO2e."""
        return self.total_co2_kg / Decimal('1000')
        
    @property
    def has_pending_physical_data(self):
        """Vérifie s'il y a des entrées carbone en attente de saisie physique."""
        return self.carbon_entries.filter(requires_physical_data=True, physical_quantity__isnull=True).exists()


class ReportAuditTrail(models.Model):
    """
    Piste d'audit pour le rapport (actions utilisateur).
    """
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='audit_trail'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True
    )
    
    ACTION_CHOICES = [
        ('created', 'Créé'),
        ('processing_started', 'Traitement démarré'),
        ('processing_completed', 'Traitement terminé'),
        ('processing_failed', 'Traitement échoué'),
        ('pdf_generated', 'PDF généré'),
        ('pdf_downloaded', 'PDF téléchargé'),
        ('ixbrl_generated', 'iXBRL généré'),
        ('ixbrl_downloaded', 'iXBRL téléchargé'),
        ('entries_viewed', 'Détails consultés'),
        ('exported', 'Exporté'),
    ]
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Audit trail rapport"
        verbose_name_plural = "Audit trails rapports"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.report} - {self.action}"

class MaterialityAssessment(models.Model):
    """
    Évaluation de la double matérialité (Impacts, Risques, Opportunités).
    Les réponses sont stockées dynamiquement en JSONB.
    """
    report = models.OneToOneField(
        Report,
        on_delete=models.CASCADE,
        related_name='materiality_assessment'
    )
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Évaluation Double Matérialité"
        verbose_name_plural = "Évaluations Double Matérialité"

    def __str__(self):
        return f"Matérialité - {self.report}"
