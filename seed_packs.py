import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ledgercarbon.settings.development')
django.setup()

from apps.credits.models import CreditPack

from apps.core.models import Cabinet
from django_tenants.utils import schema_context

packs = [
    {"name": "Pack Découverte", "credits": 5, "price_euros": 149.00},
    {"name": "Pack Pro", "credits": 20, "price_euros": 499.00},
    {"name": "Pack Illimité (Annuel)", "credits": 100, "price_euros": 1999.00},
]

for cabinet in Cabinet.objects.exclude(schema_name='public'):
    with schema_context(cabinet.schema_name):
        for p in packs:
            CreditPack.objects.get_or_create(
                name=p["name"],
                defaults={"credits": p["credits"], "price_euros": p["price_euros"]}
            )


print("Credit packs seeded successfully!")
