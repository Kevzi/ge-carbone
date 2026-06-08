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
