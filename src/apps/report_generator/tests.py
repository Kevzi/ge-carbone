from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.core.models import Cabinet
from apps.report_generator.models import Report, ReportAuditTrail
from apps.carbon_engine.models import CarbonEntry, EmissionFactor
from decimal import Decimal

User = get_user_model()

class ReportEntryAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.cabinet = Cabinet.objects.create(name="Test Cabinet", schema_name="test_schema")
        self.user = User.objects.create_user(
            username="testuser",
            password="password",
            email="test@test.com",
            cabinet=self.cabinet
        )
        self.client.force_authenticate(user=self.user)
        
        self.report = Report.objects.create(
            cabinet=self.cabinet,
            created_by=self.user,
            client_name="Test Client",
            fiscal_year=2024,
            status="completed"
        )
        
        self.emission_factor1 = EmissionFactor.objects.create(
            ademe_id="EF1",
            name="Essence",
            category="Combustibles",
            value_kg_co2_per_euro=0.5,
            value_kg_co2_per_unit=2.8,
            unit="L",
            version="2024",
            valid_from="2024-01-01",
            scope=1
        )
        
        self.entry1 = CarbonEntry.objects.create(
            report=self.report,
            fec_line_number=1,
            compte_num="606100",
            debit=1000,
            co2_kg=500,
            emission_factor=self.emission_factor1,
            dqr=3,
            mapping_method="pcg_exact",
            scope=1
        )
    
    def test_list_entries(self):
        url = reverse('report_entries_list', args=[self.report.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results'] if 'results' in response.data else response.data), 1)
        
    def test_update_entry_physical_quantity(self):
        url = reverse('report_entry_detail', args=[self.report.id, self.entry1.id])
        data = {
            "physical_quantity": "500.0000",
            "physical_unit": "L",
            "emission_factor_id": self.emission_factor1.id
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.entry1.refresh_from_db()
        self.assertEqual(self.entry1.physical_quantity, Decimal("500.0000"))
        self.assertEqual(self.entry1.physical_unit, "L")
        # 500 * 2.8 = 1400
        self.assertEqual(self.entry1.co2_kg, Decimal("1400.0000"))
        self.assertEqual(self.entry1.dqr, 1)
        self.assertEqual(self.entry1.mapping_method, "manual")
        
        self.report.refresh_from_db()
        self.assertEqual(self.report.total_co2_kg, Decimal("1400.0000"))
        
        # Check audit trail
        audit = ReportAuditTrail.objects.filter(report=self.report, action='entry_updated_physically').first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.details['new_co2_kg'], "1400.0000")
