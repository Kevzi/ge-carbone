"""
Carbon Engine models - Emission factors and carbon entries
"""
from django.db import models
from decimal import Decimal


class EmissionFactor(models.Model):
    """
    Facteur d'émission de la Base Empreinte ADEME.
    Versionné pour reproductibilité des calculs.
    """
    # ADEME identifiers
    ademe_id = models.CharField(max_length=100, verbose_name="ID ADEME")
    name = models.CharField(max_length=500, verbose_name="Nom")
    category = models.CharField(max_length=255, verbose_name="Catégorie")
    subcategory = models.CharField(max_length=255, blank=True)
    
    # Emission value
    value_kg_co2_per_euro = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        verbose_name="kg CO2e / €"
    )
    value_kg_co2_per_unit = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="kg CO2e / unité"
    )
    unit = models.CharField(max_length=50, default='€', verbose_name="Unité")
    
    # Uncertainty
    uncertainty_percent = models.IntegerField(
        default=50,
        verbose_name="Incertitude (%)"
    )
    
    # Versioning
    version = models.CharField(max_length=20, verbose_name="Version ADEME")
    valid_from = models.DateField(verbose_name="Valide depuis")
    valid_until = models.DateField(null=True, blank=True)
    
    # Scope (GHG Protocol)
    SCOPE_CHOICES = [
        (1, 'Scope 1 - Direct'),
        (2, 'Scope 2 - Indirect énergie'),
        (3, 'Scope 3 - Autres indirects'),
    ]
    scope = models.IntegerField(choices=SCOPE_CHOICES, default=3)
    
    # Metadata
    source_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Facteur d'émission"
        verbose_name_plural = "Facteurs d'émission"
        unique_together = ['ademe_id', 'version']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['scope']),
        ]

    def __str__(self):
        return f"{self.name} ({self.value_kg_co2_per_euro} kg/€)"


class PCGMapping(models.Model):
    """
    Mapping entre comptes PCG et catégories ADEME.
    """
    # PCG account
    pcg_prefix = models.CharField(
        max_length=10,
        verbose_name="Préfixe compte PCG"
    )
    pcg_description = models.CharField(max_length=255, blank=True)
    
    # ADEME mapping
    emission_factor = models.ForeignKey(
        EmissionFactor,
        on_delete=models.PROTECT,
        related_name='pcg_mappings'
    )
    
    # Priority (for cascade matching)
    priority = models.IntegerField(
        default=0,
        help_text="Plus élevé = plus prioritaire (exact match > racine)"
    )
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mapping PCG"
        verbose_name_plural = "Mappings PCG"
        ordering = ['-priority', 'pcg_prefix']

    def __str__(self):
        return f"{self.pcg_prefix} → {self.emission_factor.category}"


class CarbonEntry(models.Model):
    """
    Entrée carbone calculée à partir d'une ligne FEC.
    """
    # Relation au rapport
    report = models.ForeignKey(
        'report_generator.Report',
        on_delete=models.CASCADE,
        related_name='carbon_entries'
    )
    
    # Source FEC line
    fec_line_number = models.IntegerField(verbose_name="N° ligne FEC")
    
    # FEC data
    compte_num = models.CharField(max_length=20, verbose_name="Compte")
    compte_lib = models.CharField(max_length=255, blank=True)
    ecriture_lib = models.CharField(max_length=500, blank=True)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0'))
    
    # Carbon calculation
    emission_factor = models.ForeignKey(
        EmissionFactor,
        on_delete=models.PROTECT,
        related_name='carbon_entries',
        null=True,
        blank=True
    )
    co2_kg = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        verbose_name="kg CO2e"
    )
    
    # Quality score (Data Quality Rating)
    DQR_CHOICES = [
        (1, '1 - Très faible (fallback)'),
        (2, '2 - Faible (estimation)'),
        (3, '3 - Moyen (PCG standard)'),
        (4, '4 - Bon (NLP enrichi)'),
        (5, '5 - Excellent (donnée primaire)'),
    ]
    dqr = models.IntegerField(
        choices=DQR_CHOICES,
        default=3,
        verbose_name="Score qualité"
    )
    
    # Mapping method
    MAPPING_METHOD_CHOICES = [
        ('pcg_exact', 'PCG exact'),
        ('pcg_prefix', 'PCG préfixe'),
        ('nlp', 'NLP libellé'),
        ('manual', 'Manuel'),
        ('fallback', 'Fallback'),
    ]
    mapping_method = models.CharField(
        max_length=20,
        choices=MAPPING_METHOD_CHOICES,
        default='pcg_prefix'
    )
    
    # Scope (cached from emission_factor for aggregation)
    scope = models.IntegerField(choices=EmissionFactor.SCOPE_CHOICES, default=3)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Entrée carbone"
        verbose_name_plural = "Entrées carbone"
        ordering = ['fec_line_number']
        indexes = [
            models.Index(fields=['report', 'scope']),
            models.Index(fields=['compte_num']),
        ]

    def __str__(self):
        return f"Ligne {self.fec_line_number}: {self.co2_kg} kg CO2"
    
    @property
    def amount(self):
        """Montant net (débit - crédit)."""
        return self.debit - self.credit

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.emission_factor is None and self.co2_kg and self.co2_kg != 0:
            raise ValidationError(
                "Impossible d'avoir un bilan carbone (co2_kg != 0) sans facteur d'émission associé."
            )
