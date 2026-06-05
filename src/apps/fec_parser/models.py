"""
FEC Parser models - FECFile storage and validation
"""
from django.db import models
from django.conf import settings


class FECFile(models.Model):
    """
    Fichier FEC uploadé pour traitement.
    """
    # Relation au rapport (sera défini dans report_generator)
    # report = models.OneToOneField('report_generator.Report', ...)
    
    # File info
    original_filename = models.CharField(max_length=255, verbose_name="Nom fichier original")
    storage_path = models.CharField(max_length=500, verbose_name="Chemin S3")
    file_size_bytes = models.BigIntegerField(default=0, verbose_name="Taille (bytes)")
    
    # Parsing info
    row_count = models.IntegerField(default=0, verbose_name="Nombre de lignes")
    encoding = models.CharField(max_length=50, default='utf-8', verbose_name="Encodage détecté")
    separator = models.CharField(max_length=5, default='\t', verbose_name="Séparateur")
    
    # Validation
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('validating', 'Validation en cours'),
        ('valid', 'Valide'),
        ('invalid', 'Invalide'),
    ]
    validation_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    validation_errors = models.JSONField(default=list, blank=True)
    
    # Processing
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    processing_time_ms = models.IntegerField(default=0)
    
    # RGPD - Soft delete for data retention policy
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fichier FEC"
        verbose_name_plural = "Fichiers FEC"

    def __str__(self):
        return f"{self.original_filename} ({self.row_count} lignes)"
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None


class FECValidationRule(models.Model):
    """
    Règles de validation FEC selon Article A47 A-1.
    """
    column_name = models.CharField(max_length=50, unique=True)
    column_index = models.IntegerField()
    is_required = models.BooleanField(default=True)
    data_type = models.CharField(max_length=20)  # 'string', 'date', 'decimal'
    max_length = models.IntegerField(null=True, blank=True)
    regex_pattern = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Règle validation FEC"
        verbose_name_plural = "Règles validation FEC"
        ordering = ['column_index']

    def __str__(self):
        return f"{self.column_name} (col {self.column_index})"
