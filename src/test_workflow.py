import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ledgercarbon.settings.development")
django.setup()

from apps.fec_parser.services import FECParser
from apps.carbon_engine.services import CarbonCalculator

parser = FECParser()
file_path = "../test_fec_2024.txt"
with open(file_path, "rb") as f:
    content = f.read()

print("Parsing FEC file...")
rows = parser.parse_all(content)
print(f"Parsed {len(rows)} rows.")

calculator = CarbonCalculator()
results = calculator.calculate_batch(rows)
aggregated = calculator.aggregate_results(results)

total = aggregated["total_co2_kg"]
avg_dqr = aggregated["average_dqr"]
print(f"\nGenerated {len(results)} carbon entries.")
print(f"Total emissions: {total:.2f} kg CO2e")
print(f"Average DQR: {avg_dqr:.1f}/4.0")

print("\nSample entries (expense accounts only):")
for entry in results:
    if entry.mapping_method != "excluded":
        print(f"- Compte: {entry.compte_num} ({entry.ecriture_lib}) | DQR: {entry.dqr} | Factor: {entry.emission_factor_name} | Emissions: {entry.co2_kg:.2f} kg")
