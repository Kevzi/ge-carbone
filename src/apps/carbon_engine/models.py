"""
Carbon Engine models - Emission factors and carbon entries
"""
from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.contrib.postgres.indexes import GinIndex


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
    is_archived = models.BooleanField(
        default=False, 
        verbose_name="Archivé (donnée historique)"
    )
    
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


class InseeDeflator(models.Model):
    """
    Indice de prix de l'Insee pour ajuster l'inflation.
    Permet de déflater les montants financiers avant calcul carbone.
    """
    year = models.IntegerField(verbose_name="Année")
    naf_code = models.CharField(
        max_length=5, 
        blank=True, 
        null=True, 
        verbose_name="Code NAF (optionnel)"
    )
    index_value = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        validators=[MinValueValidator(Decimal('0.0001'))],
        verbose_name="Indice de prix"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Déflateur Insee"
        verbose_name_plural = "Déflateurs Insee"
        ordering = ['-year', 'naf_code']
        constraints = [
            models.UniqueConstraint(fields=['year'], condition=models.Q(naf_code__isnull=True), name='unique_year_global_deflator'),
            models.UniqueConstraint(fields=['year', 'naf_code'], condition=models.Q(naf_code__isnull=False), name='unique_year_naf_deflator'),
        ]

    def __str__(self):
        naf = f" ({self.naf_code})" if self.naf_code else " (Global)"
        return f"{self.year}{naf} : {self.index_value}"


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


class SireneStock(models.Model):
    """
    Base Sirene Insee stockée localement pour éviter le rate-limiting de l'API.
    """
    siren = models.CharField(max_length=9, unique=True, verbose_name="SIREN")
    denomination = models.CharField(max_length=255, verbose_name="Dénomination")
    naf_code = models.CharField(max_length=5, verbose_name="Code NAF")
    naf_2025_etablissement = models.CharField(max_length=6, null=True, blank=True, verbose_name="NAF 2025 Établissement")
    naf_2025_unite_legale = models.CharField(max_length=6, null=True, blank=True, verbose_name="NAF 2025 Unité Légale")
    
    class Meta:
        verbose_name = "Établissement Sirene"
        verbose_name_plural = "Établissements Sirene"
        indexes = [
            GinIndex(fields=['denomination'], name='sirene_denomination_gin', opclasses=['gin_trgm_ops']),
        ]

    def __str__(self):
        return f"{self.siren} - {self.denomination} ({self.naf_code})"


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
    ecriture_date = models.DateField(null=True, blank=True, verbose_name="Date d'écriture")
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
    
    # Deflator
    deflator_factor = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('1.0'),
        verbose_name="Facteur de déflation Insee"
    )
    
    # Physical data (manual entry)
    requires_physical_data = models.BooleanField(
        default=False,
        verbose_name="Saisie physique requise (hybridation)"
    )
    physical_quantity = models.DecimalField(
        max_digits=15,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name="Quantité physique"
    )
    physical_unit = models.CharField(max_length=50, blank=True)
    
    # Quality score (Data Quality Rating)
    DQR_CHOICES = [
        (1, '1 - Excellent (donnée primaire / physique)'),
        (2, '2 - Bon (Fournisseur NAF)'),
        (3, '3 - Moyen (Désambiguïsation NLP)'),
        (4, '4 - Faible (PCG exact / préfixe monétaire)'),
        (5, '5 - Très faible (fallback)'),
    ]
    dqr = models.IntegerField(
        choices=DQR_CHOICES,
        default=3,
        verbose_name="Score qualité"
    )
    
    # Mapping method
    MAPPING_METHOD_CHOICES = [
        ('hybrid_pending', 'En attente physique'),
        ('naf_supplier', 'Fournisseur (NAF)'),
        ('nlp_override', 'Désambiguïsation NLP'),
        ('pcg_exact', 'PCG exact'),
        ('pcg_prefix', 'PCG préfixe'),
        ('manual', 'Manuel'),
        ('fallback', 'Fallback'),
        ('exclusion', 'Exclu (Anti-double compte)'),
    ]
    mapping_method = models.CharField(
        max_length=20,
        choices=MAPPING_METHOD_CHOICES,
        default='pcg_prefix'
    )
    
    fournisseur_naf = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name="Code NAF fournisseur"
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

class CarbonFeedback(models.Model):
    """
    Modèle de stockage des corrections utilisateurs pour le réentraînement NLP (Boucle de feedback).
    Les données doivent être préalablement anonymisées (RGPD).
    """
    original_compte_num = models.CharField(max_length=20, verbose_name="Compte original (tronqué)")
    original_ecriture_lib = models.CharField(max_length=500, verbose_name="Libellé original (anonymisé)")
    
    # Correction manuelle
    corrected_category = models.CharField(max_length=255, verbose_name="Catégorie corrigée")
    corrected_ademe_id = models.CharField(max_length=100, blank=True, verbose_name="ID ADEME corrigé")
    corrected_dqr = models.IntegerField(default=3, verbose_name="Score DQR de la correction")
    
    # Méta-données d'apprentissage
    used_for_training = models.BooleanField(default=False, verbose_name="Déjà utilisé pour l'entraînement")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Feedback de classification"
        verbose_name_plural = "Feedbacks de classification"

    def __str__(self):
        return f"{self.original_compte_num} - {self.original_ecriture_lib[:30]} -> {self.corrected_category}"
