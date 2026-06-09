from apps.carbon_engine.models import EmissionFactor
from apps.core.models import Cabinet
from django_tenants.utils import tenant_context
import datetime

factors_to_create = [
    {
        'ademe_id': 'PHYS_ELEC',
        'name': 'Electricité (Donnée Primaire)',
        'category': 'Electricité',
        'subcategory': 'Electricité',
        'value_kg_co2_per_euro': 0,
        'value_kg_co2_per_unit': 0.052,
        'unit': 'kWh',
        'uncertainty_percent': 5,
        'version': 'v1',
        'valid_from': datetime.date(2023, 1, 1),
        'scope': 2
    },
    {
        'ademe_id': 'PHYS_GAZ',
        'name': 'Gaz Naturel (Donnée Primaire)',
        'category': 'Gaz',
        'subcategory': 'Combustible',
        'value_kg_co2_per_euro': 0,
        'value_kg_co2_per_unit': 0.227,
        'unit': 'kWh',
        'uncertainty_percent': 5,
        'version': 'v1',
        'valid_from': datetime.date(2023, 1, 1),
        'scope': 1
    },
    {
        'ademe_id': 'PHYS_DIESEL',
        'name': 'Carburant diesel (Donnée Primaire)',
        'category': 'Carburant',
        'subcategory': 'Combustible',
        'value_kg_co2_per_euro': 0,
        'value_kg_co2_per_unit': 3.16,
        'unit': 'L',
        'uncertainty_percent': 5,
        'version': 'v1',
        'valid_from': datetime.date(2023, 1, 1),
        'scope': 1
    },
    {
        'ademe_id': 'PHYS_ESSENCE',
        'name': 'Carburant essence (Donnée Primaire)',
        'category': 'Carburant',
        'subcategory': 'Combustible',
        'value_kg_co2_per_euro': 0,
        'value_kg_co2_per_unit': 2.80,
        'unit': 'L',
        'uncertainty_percent': 5,
        'version': 'v1',
        'valid_from': datetime.date(2023, 1, 1),
    },
    {
        'ademe_id': 'PHYS_WATER',
        'name': 'Eau de distribution publique (Donnée Primaire)',
        'category': 'Eau',
        'subcategory': 'Services',
        'value_kg_co2_per_euro': 0,
        'value_kg_co2_per_unit': 0.132,
        'unit': 'm3',
        'uncertainty_percent': 10,
        'version': 'v1',
        'valid_from': datetime.date(2023, 1, 1),
        'scope': 3
    },
    {
        'ademe_id': 'PHYS_FIOUL',
        'name': 'Fioul domestique (Donnée Primaire)',
        'category': 'Carburant',
        'subcategory': 'Combustible',
        'value_kg_co2_per_euro': 0,
        'value_kg_co2_per_unit': 3.15,
        'unit': 'L',
        'uncertainty_percent': 5,
        'version': 'v1',
        'valid_from': datetime.date(2023, 1, 1),
        'scope': 1
    },
    {
        'ademe_id': 'PHYS_GPL',
        'name': 'GPL Carburant (Donnée Primaire)',
        'category': 'Carburant',
        'subcategory': 'Combustible',
        'value_kg_co2_per_euro': 0,
        'value_kg_co2_per_unit': 1.86,
        'unit': 'L',
        'uncertainty_percent': 5,
        'version': 'v1',
        'valid_from': datetime.date(2023, 1, 1),
        'scope': 1
    },
    {
        'ademe_id': 'PHYS_PROPANE',
        'name': 'Propane / Butane (Donnée Primaire)',
        'category': 'Gaz',
        'subcategory': 'Combustible',
        'value_kg_co2_per_euro': 0,
        'value_kg_co2_per_unit': 3.3,
        'unit': 'kg',
        'uncertainty_percent': 5,
        'version': 'v1',
        'valid_from': datetime.date(2023, 1, 1),
        'scope': 1
    },
    {
        'ademe_id': 'PHYS_PELLETS',
        'name': 'Granulés de bois / Pellets (Donnée Primaire)',
        'category': 'Biomasse',
        'subcategory': 'Combustible',
        'value_kg_co2_per_euro': 0,
        'value_kg_co2_per_unit': 0.03,
        'unit': 'kg',
        'uncertainty_percent': 20,
        'version': 'v1',
        'valid_from': datetime.date(2023, 1, 1),
        'scope': 1
    },
    {
        'ademe_id': 'PHYS_WOOD',
        'name': 'Bois bûche (Donnée Primaire)',
        'category': 'Biomasse',
        'subcategory': 'Combustible',
        'value_kg_co2_per_euro': 0,
        'value_kg_co2_per_unit': 0.015,
        'unit': 'kg',
        'uncertainty_percent': 30,
        'version': 'v1',
        'valid_from': datetime.date(2023, 1, 1),
        'scope': 1
    },
    {
        'ademe_id': 'PHYS_HEATNET',
        'name': 'Réseau de chaleur urbain moyen (Donnée Primaire)',
        'category': 'Chaleur',
        'subcategory': 'Réseau',
        'value_kg_co2_per_euro': 0,
        'value_kg_co2_per_unit': 0.109,
        'unit': 'kWh',
        'uncertainty_percent': 10,
        'version': 'v1',
        'valid_from': datetime.date(2023, 1, 1),
        'scope': 2
    },
    {
        'ademe_id': 'PHYS_COLDNET',
        'name': 'Réseau de froid urbain moyen (Donnée Primaire)',
        'category': 'Froid',
        'subcategory': 'Réseau',
        'value_kg_co2_per_euro': 0,
        'value_kg_co2_per_unit': 0.05,
        'unit': 'kWh',
        'uncertainty_percent': 10,
        'version': 'v1',
        'valid_from': datetime.date(2023, 1, 1),
        'scope': 2
    },
    {
        'ademe_id': 'PHYS_E85',
        'name': 'Superéthanol E85 (Donnée Primaire)',
        'category': 'Carburant',
        'subcategory': 'Combustible',
        'value_kg_co2_per_euro': 0,
        'value_kg_co2_per_unit': 1.2,
        'unit': 'L',
        'uncertainty_percent': 10,
        'version': 'v1',
        'valid_from': datetime.date(2023, 1, 1),
        'scope': 1
    }
]

cabinets = Cabinet.objects.exclude(schema_name='public')
for cabinet in cabinets:
    try:
        with tenant_context(cabinet):
            for data in factors_to_create:
                EmissionFactor.objects.update_or_create(
                    ademe_id=data['ademe_id'],
                    version=data['version'],
                    defaults=data
                )
            print(f"Seeded for {cabinet.name}")
    except Exception as e:
        print(f"Error seeding for {cabinet.name}: {e}")

print("Seeding complete.")
