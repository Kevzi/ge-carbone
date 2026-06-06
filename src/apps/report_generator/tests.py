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

    def test_export_csv(self):
        url = reverse('report_export_csv', args=[self.report.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertTrue('attachment; filename="piste_audit' in response['Content-Disposition'])
        
        # Read streaming content
        content = b''.join(response.streaming_content).decode('utf-8')
        
        # Check header
        self.assertIn('Ligne FEC,Date,Compte,Libellé,Débit,Crédit,Facteur Emission,CO2e (kg),DQR', content)
        # Check data row
        self.assertIn('1,,606100,,1000.00,0.00,Essence,500.00,3', content)

class MaterialityAssessmentAPITest(TestCase):
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
        self.url = reverse('materiality_assessment_detail', args=[self.report.id])
        
    def test_create_and_get_materiality_assessment(self):
        # Initial GET should return 404 or empty because it's not created yet
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # POST to create
        data = {
            "data": {
                "impacts": [{"id": "E1", "score": 4}],
                "risks": [{"id": "S1", "score": 3}]
            }
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data']['impacts'][0]['score'], 4)
        
        # GET should now return the data
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['risks'][0]['score'], 3)
        
    def test_update_materiality_assessment(self):
        from apps.report_generator.models import MaterialityAssessment
        assessment = MaterialityAssessment.objects.create(
            report=self.report,
            data={"initial": "data"}
        )
        
        # PATCH to update
        update_data = {
            "data": {
                "updated": "value"
            }
        }
        response = self.client.patch(self.url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        assessment.refresh_from_db()
        self.assertEqual(assessment.data.get("updated"), "value")

    def test_matrix_computation(self):
        # Test POST
        data = {
            "data": {
                "E1_1": 3,
                "E2_1": 4,
                "E3_1": 2,
                "S1_1": 4,
                "S2_1": True,
                "G1_1": False,
                "G2_1": 2
            }
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        computed = response.data['data'].get('computed_matrix')
        self.assertIsNotNone(computed)
        self.assertEqual(len(computed), 3)
        
        e_topic = next(t for t in computed if t['topic'] == 'Environnement')
        self.assertEqual(e_topic['impact'], 3.5)
        self.assertEqual(e_topic['financial'], 2.0)
        self.assertTrue(e_topic['is_material'])
        
        s_topic = next(t for t in computed if t['topic'] == 'Social')
        self.assertEqual(s_topic['impact'], 4.0)
        self.assertEqual(s_topic['financial'], 1.0)
        self.assertTrue(s_topic['is_material'])
        
        g_topic = next(t for t in computed if t['topic'] == 'Gouvernance')
        self.assertEqual(g_topic['impact'], 2.0)
        self.assertEqual(g_topic['financial'], 4.0)
        self.assertTrue(g_topic['is_material'])
        
        # Test PATCH update
        update_data = {
            "data": {
                "E1_1": 1,
                "E2_1": 1
            }
        }
        response = self.client.patch(self.url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        computed = response.data['data'].get('computed_matrix')
        e_topic = next(t for t in computed if t['topic'] == 'Environnement')
        self.assertEqual(e_topic['impact'], 1.0)
        self.assertEqual(e_topic['financial'], 2.0)
        self.assertFalse(e_topic['is_material'])


class MaterialityAssessmentModelTest(TestCase):
    def setUp(self):
        self.cabinet = Cabinet.objects.create(name="Test Cabinet", schema_name="test_schema")
        self.report = Report.objects.create(
            cabinet=self.cabinet,
            client_name="Test Client",
            fiscal_year=2024,
            status="completed"
        )

    def test_jsonfield_storage(self):
        from apps.report_generator.models import MaterialityAssessment
        test_data = {
            "impacts": [{"id": "E1", "score": 4}],
            "risks": [{"id": "S1", "score": 3}],
            "nested": {"deep": {"value": True}}
        }
        assessment = MaterialityAssessment.objects.create(
            report=self.report,
            data=test_data
        )
        
        # Reload from DB to ensure JSON serialization/deserialization works
        assessment.refresh_from_db()
        
        self.assertEqual(assessment.data["impacts"][0]["score"], 4)
        self.assertTrue(assessment.data["nested"]["deep"]["value"])
        self.assertEqual(assessment.data, test_data)
