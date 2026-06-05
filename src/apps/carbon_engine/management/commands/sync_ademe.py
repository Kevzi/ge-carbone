import logging
from django.core.management.base import BaseCommand
from apps.carbon_engine.services.ademe import ADEMESync, ADEMEAPIError
from django_tenants.utils import get_tenant_model, tenant_context

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Synchronise les facteurs d'émission avec l'API ADEME Base Empreinte pour tous les locataires"

    def add_arguments(self, parser):
        parser.add_argument(
            '--snapshot-version',
            dest='version',
            type=str,
            help='Identifiant de snapshot/millésime optionnel (ex: 2026-Q1). Par défaut, utilise un timestamp.',
        )

    def handle(self, *args, **options):
        version = options.get('version')
        service = ADEMESync()
        
        TenantModel = get_tenant_model()
        tenants = TenantModel.objects.exclude(schema_name='public')
        
        self.stdout.write(self.style.NOTICE(f'Début de la synchronisation avec la Base Empreinte ADEME pour {tenants.count()} locataires...'))
        
        for tenant in tenants:
            self.stdout.write(f'  -> Synchronisation pour le locataire : {tenant.schema_name}')
            with tenant_context(tenant):
                try:
                    count = service.sync_factors(version=version)
                    self.stdout.write(
                        self.style.SUCCESS(f'     Succès : {count} facteurs importés/mis à jour.')
                    )
                except ADEMEAPIError as e:
                    self.stderr.write(self.style.ERROR(f'     Erreur de synchronisation : {str(e)}'))
                    logger.error(f'Erreur de synchronisation ADEME via commande pour {tenant.schema_name}: {str(e)}')
