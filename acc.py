from apps.report_generator.models import Report
from apps.carbon_engine.models import CarbonEntry, CarbonFeedback
from django.db import connection
from apps.core.models import Cabinet
from django_tenants.utils import tenant_context

total_nlp = 0
total_feedbacks = 0

for cabinet in Cabinet.objects.exclude(schema_name='public'):
    try:
        with tenant_context(cabinet):
            nlp_entries = CarbonEntry.objects.filter(mapping_method__in=['nlp_override', 'manual']).count()
            feedbacks = CarbonFeedback.objects.count()
            
            total_nlp += nlp_entries
            total_feedbacks += feedbacks
    except Exception as e:
        pass

if total_nlp > 0:
    accuracy = (total_nlp - total_feedbacks) / total_nlp * 100
    print(f"Total NLP entries: {total_nlp}")
    print(f"Total feedbacks (corrections): {total_feedbacks}")
    print(f"Accuracy: {accuracy:.2f}%")
else:
    print("No NLP entries found.")
