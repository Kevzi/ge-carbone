import logging
from django.core.management.base import BaseCommand
from apps.carbon_engine.models import InseeDeflator

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Charge les données factices/réelles des déflateurs Insee pour ajuster l\'inflation.'

    def handle(self, *args, **options):
        self.stdout.write("Chargement des déflateurs Insee...")

        # Valeurs basées sur une estimation de l'indice des prix à la consommation (IPC) en France
        # Base 100 en 2015
        deflators = [
            {"year": 2015, "index": 100.0},
            {"year": 2016, "index": 100.2},
            {"year": 2017, "index": 101.2},
            {"year": 2018, "index": 103.1},
            {"year": 2019, "index": 104.2},
            {"year": 2020, "index": 104.7},
            {"year": 2021, "index": 106.4},
            {"year": 2022, "index": 112.0},
            {"year": 2023, "index": 117.5},
            {"year": 2024, "index": 120.0},
            {"year": 2025, "index": 122.0},
            {"year": 2026, "index": 124.0},
        ]

        count = 0
        for data in deflators:
            obj, created = InseeDeflator.objects.update_or_create(
                year=data["year"],
                naf_code=None,  # Déflateur global par défaut
                defaults={
                    'index_value': data["index"]
                }
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Succès : {count} déflateurs ajoutés (total: {len(deflators)}).'))
