from apps.core.models import User
from apps.report_generator.models import Report

for u in User.objects.all():
    cab = u.cabinet
    rc = cab.reports.count() if cab else 0
    print(f"User: {u.username}, Cabinet: {cab.name if cab else 'None'}, Reports: {rc}")

print(f"Total reports: {Report.objects.count()}")
