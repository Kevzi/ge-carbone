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
import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
import apps.report_generator.services
import apps.report_generator.tasks

class TestXBRLValidation(unittest.TestCase):

    @patch('apps.report_generator.services.CntlrCmdLine.CntlrCmdLine')
    def test_xbrl_validator_service_success(self, mock_cntlr_class):
        from apps.report_generator.services import XBRLValidatorService
        
        # Setup mock controller: parseAndRun must return 0 (success)
        mock_instance = mock_cntlr_class.return_value
        mock_instance.parseAndRun.return_value = 0
        
        # Execute service with a real temp file (path validation requires existence)
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            validator = XBRLValidatorService()
            is_valid, details = validator.validate_file(tmp_path)
            
            self.assertTrue(is_valid)
            self.assertEqual(details["total_errors"], 0)
            self.assertEqual(details["validated_against"], XBRLValidatorService.ESRS_ENTRY_POINT)
            self.assertEqual(details["exit_code"], 0)
            
            # Verify Arelle was called with correct tokens (F2 fix: two separate tokens)
            mock_instance.parseAndRun.assert_called_once()
            call_args = mock_instance.parseAndRun.call_args[0][0]
            self.assertIn("--formula", call_args)
            self.assertIn("run", call_args)
            # F1 fix: verify ESRS entry point was passed
            self.assertIn("--importFile", call_args)
            self.assertIn(XBRLValidatorService.ESRS_ENTRY_POINT, call_args)
        finally:
            os.unlink(tmp_path)

    @patch('apps.report_generator.tasks.Report.objects.get')
    @patch('apps.report_generator.tasks.XBRLValidatorService')
    def test_validate_esrs_xbrl_task(self, mock_validator_class, mock_report_get):
        from apps.report_generator.tasks import validate_esrs_xbrl_task
        
        # Mock Report
        mock_report = MagicMock()
        mock_report_get.return_value = mock_report
        
        # Mock Validator
        mock_validator = mock_validator_class.return_value
        mock_validator.validate_file.return_value = (False, {"total_errors": 1, "errors": []})
        
        # F4 fix: use a real temp file so path existence check passes
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            validate_esrs_xbrl_task(123, tmp_path)
            
            # Verify Report model was updated and saved with update_fields (F5)
            mock_report_get.assert_called_once_with(id=123)
            self.assertFalse(mock_report.xbrl_validation_passed)
            mock_report.save.assert_called_once()
            save_kwargs = mock_report.save.call_args[1]
            self.assertIn('xbrl_validation_passed', save_kwargs.get('update_fields', []))
            self.assertIn('xbrl_validation_errors', save_kwargs.get('update_fields', []))
        finally:
            os.unlink(tmp_path)

class TestIXBRL(unittest.TestCase):
    def test_ixbrl_generator_service(self):
        from apps.report_generator.services import IXBRLGeneratorService
        report = MagicMock()
        report.id = 1
        report.client_name = "Test Client"
        report.fiscal_year = 2023
        report.scope1_co2_kg = 100
        report.scope2_co2_kg = 200
        report.scope3_co2_kg = 300
        report.total_co2_kg = 600
        report.client_siret = "12345678901234"
        report.average_dqr = 2.5
        
        # mock materiality
        mock_mat = MagicMock()
        mock_mat.data = {"impacts": [{"score": 3}]}
        report.materiality_assessment = mock_mat
        
        generator = IXBRLGeneratorService()
        html = generator.generate(report)
        
        self.assertIn("xmlns:ix=\"http://www.xbrl.org/2013/inlineXBRL\"", html)
        self.assertIn("<ix:header>", html)
        self.assertIn("esrs_all.xsd", html)
        self.assertIn("esrs:GrossScope1GreenhouseGasEmissions", html)

    def test_ixbrl_article_8_generation(self):
        from apps.report_generator.services import IXBRLGeneratorService
        report = MagicMock()
        report.id = 2
        report.client_name = "Test Client"
        report.fiscal_year = 2023
        
        generator = IXBRLGeneratorService()
        html = generator.generate(report, include_article8=True)
        
        self.assertIn('xmlns:art8=', html)
        self.assertIn('https://xbrl.efrag.org/taxonomy/article8/2023-12-22', html)

    def test_ixbrl_article_8_excluded(self):
        from apps.report_generator.services import IXBRLGeneratorService
        report = MagicMock()
        report.id = 3
        report.client_name = "Test Client"
        report.fiscal_year = 2023
        
        generator = IXBRLGeneratorService()
        html = generator.generate(report, include_article8=False)
        
        self.assertNotIn('xmlns:art8=', html)

    @patch('apps.report_generator.tasks.validate_esrs_xbrl_task.delay')
    @patch('apps.report_generator.tasks.Report.objects.get')
    def test_generate_ixbrl_task(self, mock_report_get, mock_validate_delay):
        from apps.report_generator.tasks import generate_ixbrl_task
        
        mock_report = MagicMock()
        mock_report.id = 456
        mock_report.status = 'completed'
        mock_report_get.return_value = mock_report
        
        generate_ixbrl_task(456)
        
        mock_report_get.assert_called_once_with(id=456)
        mock_report.save.assert_called()
        self.assertTrue(mock_report.ixbrl_url.endswith('.html'))
        self.assertIsNotNone(mock_report.ixbrl_generated_at)
        
        # Ensure validation is chained
        mock_validate_delay.assert_called_once_with(456, mock_report.ixbrl_url)

class ReportExportCreditIntegrationTest(TestCase):
    def setUp(self):
        from apps.core.models import CreditBalance
        self.client = APIClient()
        self.cabinet = Cabinet.objects.create(name="Test Cabinet 3", schema_name="test_schema_3")
        self.user = User.objects.create_user(
            username="testuser3",
            password="password",
            email="test3@test.com",
            cabinet=self.cabinet
        )
        self.client.force_authenticate(user=self.user)
        
        self.report = Report.objects.create(
            cabinet=self.cabinet,
            created_by=self.user,
            client_name="Test Client 3",
            fiscal_year=2024,
            status="completed"
        )
        CreditBalance.objects.create(cabinet=self.cabinet, balance=0)

    def test_pdf_export_insufficient_credits(self):
        url = reverse('report_pdf', args=[self.report.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(response.data['error'], 'Insufficient credits')

    def test_ixbrl_export_insufficient_credits(self):
        url = reverse('report_ixbrl', args=[self.report.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        
    @patch('apps.report_generator.services.PDFReportGenerator')
    def test_pdf_export_with_credits(self, mock_pdf_gen):
        self.cabinet.credit_balance.balance = 1
        self.cabinet.credit_balance.save()
        
        mock_instance = mock_pdf_gen.return_value
        mock_instance.generate_pdf.return_value = b'%PDF-1.4 mock pdf content'
        
        url = reverse('report_pdf', args=[self.report.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.report.refresh_from_db()
        self.assertTrue(self.report.is_unlocked)
        self.cabinet.credit_balance.refresh_from_db()
        self.assertEqual(self.cabinet.credit_balance.balance, 0)

    def test_pdf_export_fails_if_cannot_consume_credits(self):
        self.cabinet.credit_balance.balance = 5
        self.cabinet.credit_balance.save()
        self.user.can_consume_credits = False
        self.user.save()
        
        url = reverse('report_pdf', args=[self.report.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        
        self.report.refresh_from_db()
        self.assertFalse(self.report.is_unlocked)
        self.cabinet.credit_balance.refresh_from_db()
        self.assertEqual(self.cabinet.credit_balance.balance, 5)
