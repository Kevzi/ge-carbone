from apps.carbon_engine.models import EmissionFactor
factors = EmissionFactor.objects.filter(value_kg_co2_per_unit__isnull=False)
print("Physical Factors count:", factors.count())
for f in factors:
    print(f.id, f.name, f.unit)
