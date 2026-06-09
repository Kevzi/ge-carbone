"""
Management command to seed initial emission factors and PCG mappings.
Usage: python manage.py seed_emission_factors
"""
from django.core.management.base import BaseCommand
from apps.carbon_engine.models import EmissionFactor, PCGMapping
from decimal import Decimal
from datetime import date


class Command(BaseCommand):
    help = 'Seed initial emission factors from ADEME Base Empreinte'

    def handle(self, *args, **options):
        self.stdout.write('Seeding emission factors...')
        
        # Create emission factors
        factors = [
            # Scope 1 - Direct emissions
            {
                'ademe_id': 'FE_CARBURANT_DIESEL',
                'name': 'Carburant diesel',
                'category': 'Énergie',
                'value_kg_co2_per_euro': Decimal('2.51'),
                'value_kg_co2_per_unit': Decimal('3.16'),
                'unit': 'L',
                'scope': 1,
                'version': '2024.1',
            },
            {
                'ademe_id': 'FE_CARBURANT_ESSENCE',
                'name': 'Carburant essence',
                'category': 'Énergie',
                'value_kg_co2_per_euro': Decimal('2.28'),
                'value_kg_co2_per_unit': Decimal('2.80'),
                'unit': 'L',
                'scope': 1,
                'version': '2024.1',
            },
            {
                'ademe_id': 'FE_GAZ_NATUREL',
                'name': 'Gaz naturel',
                'category': 'Énergie',
                'value_kg_co2_per_euro': Decimal('0.20'),
                'value_kg_co2_per_unit': Decimal('0.20'),
                'unit': 'kWh',
                'scope': 1,
                'version': '2024.1',
            },
            
            # Scope 2 - Indirect energy
            {
                'ademe_id': 'FE_ELECTRICITE_FR',
                'name': 'Électricité France',
                'category': 'Énergie',
                'value_kg_co2_per_euro': Decimal('0.05'),
                'value_kg_co2_per_unit': Decimal('0.05'),
                'unit': 'kWh',
                'scope': 2,
                'version': '2024.1',
            },
            
            # Scope 3 - Other indirect
            {
                'ademe_id': 'FE_TRANSPORT_FERROVIAIRE',
                'name': 'Transport ferroviaire France',
                'category': 'Transport',
                'value_kg_co2_per_euro': Decimal('0.03'),
                'value_kg_co2_per_unit': Decimal('0.003'),
                'unit': 'km',
                'scope': 3,
                'version': '2024.1',
            },
            {
                'ademe_id': 'FE_TRANSPORT_AERIEN_COURT',
                'name': 'Transport aérien court courrier',
                'category': 'Transport',
                'value_kg_co2_per_euro': Decimal('0.25'),
                'value_kg_co2_per_unit': Decimal('0.258'),
                'unit': 'km',
                'scope': 3,
                'version': '2024.1',
            },
            {
                'ademe_id': 'FE_TRANSPORT_AERIEN_LONG',
                'name': 'Transport aérien long courrier',
                'category': 'Transport',
                'value_kg_co2_per_euro': Decimal('0.18'),
                'value_kg_co2_per_unit': Decimal('0.152'),
                'unit': 'km',
                'scope': 3,
                'version': '2024.1',
            },
            {
                'ademe_id': 'FE_TRANSPORT_ROUTIER',
                'name': 'Transport routier marchandises',
                'category': 'Transport',
                'value_kg_co2_per_euro': Decimal('0.12'),
                'value_kg_co2_per_unit': Decimal('0.120'),
                'unit': 'km',
                'scope': 3,
                'version': '2024.1',
            },
            {
                'ademe_id': 'FE_HEBERGEMENT_HOTEL',
                'name': 'Hébergement hôtelier',
                'category': 'Services',
                'value_kg_co2_per_euro': Decimal('0.02'),
                'value_kg_co2_per_unit': Decimal('15.0'),
                'unit': 'nuit',
                'scope': 3,
                'version': '2024.1',
            },
            {
                'ademe_id': 'FE_RESTAURATION',
                'name': 'Restauration',
                'category': 'Services',
                'value_kg_co2_per_euro': Decimal('0.50'),
                'value_kg_co2_per_unit': Decimal('5.5'),
                'unit': 'repas',
                'scope': 3,
                'version': '2024.1',
            },
            {
                'ademe_id': 'FE_CLOUD_COMPUTING',
                'name': 'Cloud computing',
                'category': 'Numérique',
                'value_kg_co2_per_euro': Decimal('0.08'),
                'scope': 3,
                'version': '2024.1',
            },
            {
                'ademe_id': 'FE_EQUIPEMENT_IT',
                'name': 'Équipement informatique',
                'category': 'Numérique',
                'value_kg_co2_per_euro': Decimal('0.50'),
                'value_kg_co2_per_unit': Decimal('150.0'),
                'unit': 'unité',
                'scope': 3,
                'version': '2024.1',
            },
            {
                'ademe_id': 'FE_PAPIER_BUREAU',
                'name': 'Papier bureau',
                'category': 'Fournitures',
                'value_kg_co2_per_euro': Decimal('0.80'),
                'value_kg_co2_per_unit': Decimal('0.80'),
                'unit': 'kg',
                'scope': 3,
                'version': '2024.1',
            },
            {
                'ademe_id': 'FE_FOURNITURES_BUREAU',
                'name': 'Fournitures de bureau',
                'category': 'Fournitures',
                'value_kg_co2_per_euro': Decimal('0.15'),
                'scope': 3,
                'version': '2024.1',
            },
            {
                'ademe_id': 'FE_SERVICES_GENERAUX',
                'name': 'Services généraux',
                'category': 'Services',
                'value_kg_co2_per_euro': Decimal('0.08'),
                'scope': 3,
                'version': '2024.1',
            },
        ]
        
        created_count = 0
        for factor_data in factors:
            factor, created = EmissionFactor.objects.update_or_create(
                ademe_id=factor_data['ademe_id'],
                defaults={
                    **factor_data,
                    'valid_from': date(2024, 1, 1),
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} emission factors')
        )
        
        # Create PCG mappings
        self.stdout.write('Seeding PCG mappings...')
        
        # Get factors for mapping
        transport_fer = EmissionFactor.objects.filter(ademe_id='FE_TRANSPORT_FERROVIAIRE').first()
        transport_aerien = EmissionFactor.objects.filter(ademe_id='FE_TRANSPORT_AERIEN_COURT').first()
        fournitures = EmissionFactor.objects.filter(ademe_id='FE_FOURNITURES_BUREAU').first()
        services = EmissionFactor.objects.filter(ademe_id='FE_SERVICES_GENERAUX').first()
        
        mappings = []
        
        if transport_fer:
            mappings.append({'pcg_prefix': '6251', 'emission_factor': transport_fer, 'priority': 10})
        if transport_aerien:
            mappings.append({'pcg_prefix': '6256', 'emission_factor': transport_aerien, 'priority': 10})
        if fournitures:
            mappings.append({'pcg_prefix': '6061', 'emission_factor': fournitures, 'priority': 10})
            mappings.append({'pcg_prefix': '6064', 'emission_factor': fournitures, 'priority': 10})
        if services:
            mappings.append({'pcg_prefix': '61', 'emission_factor': services, 'priority': 1})
            mappings.append({'pcg_prefix': '62', 'emission_factor': services, 'priority': 1})
        
        mapping_count = 0
        for mapping_data in mappings:
            mapping, created = PCGMapping.objects.update_or_create(
                pcg_prefix=mapping_data['pcg_prefix'],
                defaults=mapping_data
            )
            if created:
                mapping_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {mapping_count} PCG mappings')
        )
        
        self.stdout.write(self.style.SUCCESS('Seeding complete!'))
