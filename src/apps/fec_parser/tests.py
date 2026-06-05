"""
Tests for FEC Parser services.
"""
import pytest
from decimal import Decimal
from apps.fec_parser.services import FECValidator, FECParser, FECRow


class TestFECValidator:
    """Tests for FECValidator."""
    
    def test_detect_encoding_utf8(self):
        validator = FECValidator()
        content = "JournalCode\tJournalLib\n".encode('utf-8')
        assert validator.detect_encoding(content) == 'utf-8'
    
    def test_detect_separator_tab(self):
        validator = FECValidator()
        line = "JournalCode\tJournalLib\tEcritureNum"
        assert validator.detect_separator(line) == '\t'
    
    def test_detect_separator_pipe(self):
        validator = FECValidator()
        line = "JournalCode|JournalLib|EcritureNum"
        assert validator.detect_separator(line) == '|'
    
    def test_parse_date_yyyymmdd(self):
        validator = FECValidator()
        result = validator.parse_date('20231215')
        assert result is not None
        assert result.year == 2023
        assert result.month == 12
        assert result.day == 15
    
    def test_parse_date_french(self):
        validator = FECValidator()
        result = validator.parse_date('15/12/2023')
        assert result is not None
        assert result.year == 2023
    
    def test_parse_decimal_french_format(self):
        validator = FECValidator()
        result = validator.parse_decimal('1234,56')
        assert result == Decimal('1234.56')
    
    def test_parse_decimal_with_spaces(self):
        validator = FECValidator()
        result = validator.parse_decimal('1 234,56')
        assert result == Decimal('1234.56')
    
    def test_validate_empty_file(self):
        validator = FECValidator()
        result = validator.validate(b'')
        assert not result.is_valid
        assert result.error_count > 0
    
    def test_validate_valid_fec(self):
        validator = FECValidator()
        fec_content = (
            "JournalCode\tJournalLib\tEcritureNum\tEcritureDate\tCompteNum\t"
            "CompteLib\tCompAuxNum\tCompAuxLib\tPieceRef\tPieceDate\t"
            "EcritureLib\tDebit\tCredit\tEcritureLet\tDateLet\tValidDate\t"
            "Montantdevise\tIdevise\n"
            "VE\tVentes\t001\t20231201\t411000\tClients\t\t\tFV001\t20231201\t"
            "Facture client\t1000,00\t0,00\t\t\t20231201\t\t\n"
        ).encode('utf-8')
        
        result = validator.validate(fec_content)
        assert result.is_valid
        assert result.row_count == 1
        assert result.encoding == 'utf-8'
    
    def test_validate_missing_column(self):
        validator = FECValidator()
        # Missing CompteNum
        fec_content = (
            "JournalCode\tJournalLib\tEcritureNum\n"
            "VE\tVentes\t001\n"
        ).encode('utf-8')
        
        result = validator.validate(fec_content)
        assert not result.is_valid
        assert any(e.error_type == 'missing_column' for e in result.errors)


class TestFECParser:
    """Tests for FECParser."""
    
    def test_parse_single_row(self):
        parser = FECParser()
        fec_content = (
            "JournalCode\tJournalLib\tEcritureNum\tEcritureDate\tCompteNum\t"
            "CompteLib\tCompAuxNum\tCompAuxLib\tPieceRef\tPieceDate\t"
            "EcritureLib\tDebit\tCredit\tEcritureLet\tDateLet\tValidDate\t"
            "Montantdevise\tIdevise\n"
            "VE\tVentes\t001\t20231201\t411000\tClients\t\t\tFV001\t20231201\t"
            "Facture client\t1000,00\t0,00\t\t\t20231201\t\t\n"
        ).encode('utf-8')
        
        import io
        fec_file = io.BytesIO(fec_content)
        rows = parser.parse_all(fec_file)
        assert len(rows) == 1
        
        row = rows[0]
        assert row.journal_code == 'VE'
        assert row.compte_num == '411000'
        assert row.debit == Decimal('1000.00')
        assert row.credit == Decimal('0.00')
    
    def test_parse_streaming(self):
        parser = FECParser(chunk_size=2)
        
        # Create FEC with multiple rows
        header = (
            "JournalCode\tJournalLib\tEcritureNum\tEcritureDate\tCompteNum\t"
            "CompteLib\tCompAuxNum\tCompAuxLib\tPieceRef\tPieceDate\t"
            "EcritureLib\tDebit\tCredit\tEcritureLet\tDateLet\tValidDate\t"
            "Montantdevise\tIdevise\n"
        )
        row_template = (
            "VE\tVentes\t{num}\t20231201\t411000\tClients\t\t\tFV{num}\t20231201\t"
            "Facture\t100,00\t0,00\t\t\t20231201\t\t\n"
        )
        
        content = header + "".join(row_template.format(num=i) for i in range(5))
        
        import io
        fec_file = io.BytesIO(content.encode('utf-8'))
        chunks = list(parser.parse_streaming(fec_file))
        
        # Should have 3 chunks: [2, 2, 1] rows
        assert len(chunks) == 3
        assert len(chunks[0]) == 2
        assert len(chunks[1]) == 2
        assert len(chunks[2]) == 1


@pytest.mark.django_db
class TestTenantModels:
    """Tests for FECFile and CarbonEntry within a tenant context."""
    
    def test_create_fec_file_and_carbon_entry_in_tenant(self):
        from apps.core.models import Cabinet
        from apps.fec_parser.models import FECFile
        from apps.carbon_engine.models import CarbonEntry
        from apps.report_generator.models import Report
        from django_tenants.utils import tenant_context
        from django.db import connection
        
        # Create a tenant (automatically creates schema and runs migrations)
        cabinet = Cabinet.objects.create(
            schema_name='test_tenant_fec',
            name='Cabinet FEC Test',
        )
        
        # Activating the tenant context
        with tenant_context(cabinet):
            # Assert schema is active
            assert connection.schema_name == 'test_tenant_fec'
            
            # Create a report and FEC File (needed for CarbonEntry)
            report = Report.objects.create(
                cabinet=cabinet,
                client_name='Test Client',
                fiscal_year=2023,
                status='draft'
            )
            
            fec_file = FECFile.objects.create(
                original_filename='test.txt',
                validation_status='valid'
            )
            
            # Create a Carbon Entry
            entry = CarbonEntry.objects.create(
                report=report,
                fec_line_number=1,
                compte_num='411000',
                co2_kg=Decimal('0')  # No emission factor needed since co2_kg is 0
            )
            
            # Verify they exist
            assert FECFile.objects.count() == 1
            assert CarbonEntry.objects.count() == 1
            assert entry.fec_line_number == 1


@pytest.mark.django_db
class TestFECUploadAPI:
    """Tests for the FEC Upload API Endpoint."""
    
    def test_upload_missing_file(self):
        from rest_framework.test import APIClient
        from django.urls import reverse
        from apps.core.models import Cabinet, User, Domain
        from django_tenants.utils import tenant_context
        
        cabinet = Cabinet.objects.create(schema_name='test_api_tenant', name='API Test')
        Domain.objects.create(domain='testserver', tenant=cabinet, is_primary=True)
        with tenant_context(cabinet):
            user = User.objects.create_user(username='test_user', password='pwd', cabinet=cabinet)
            client = APIClient()
            client.force_authenticate(user=user)
            
            # The URL name will be 'fec-upload'
            url = reverse('fec-upload')
            response = client.post(url, {}, format='multipart')
            
            assert response.status_code == 400
            assert 'file' in response.data or 'error' in response.data

    def test_upload_valid_file(self, tmp_path):
        from rest_framework.test import APIClient
        from django.urls import reverse
        from apps.core.models import Cabinet, User, Domain
        from apps.fec_parser.models import FECFile
        from apps.report_generator.models import Report
        from django_tenants.utils import tenant_context
        from django.core.files.uploadedfile import SimpleUploadedFile
        import os
        
        cabinet = Cabinet.objects.create(schema_name='test_api_tenant_2', name='API Test 2')
        Domain.objects.create(domain='testserver', tenant=cabinet, is_primary=True)
        with tenant_context(cabinet):
            user = User.objects.create_user(username='test_user', password='pwd', cabinet=cabinet)
            
            # Create an initial report to attach the FEC to
            report = Report.objects.create(
                cabinet=cabinet,
                created_by=user,
                client_name='Client A',
                fiscal_year=2023,
                status='pending'
            )
            
            client = APIClient()
            client.force_authenticate(user=user)
            
            fec_content = (
                b"JournalCode\tJournalLib\tEcritureNum\tEcritureDate\tCompteNum\t"
                b"CompteLib\tCompAuxNum\tCompAuxLib\tPieceRef\tPieceDate\t"
                b"EcritureLib\tDebit\tCredit\tEcritureLet\tDateLet\tValidDate\t"
                b"Montantdevise\tIdevise\n"
                b"VE\tVentes\t001\t20231201\t411000\tClients\t\t\tFV001\t20231201\t"
                b"Facture client\t1000,00\t0,00\t\t\t20231201\t\t\n"
            )
            uploaded_file = SimpleUploadedFile("test_fec.txt", fec_content, content_type="text/plain")
            
            url = reverse('fec-upload')
            
            with __import__('unittest').mock.patch('apps.carbon_engine.tasks.enrich_fec_nlp_task.delay') as mock_nlp_delay:
                response = client.post(url, {'file': uploaded_file, 'report_id': report.id}, format='multipart')
                
                # Should be accepted and processed (sync celery due to eager)
                assert response.status_code == 202
                
                # Verify that the NLP task was chained
                mock_nlp_delay.assert_called_once_with(report.id, 'test_api_tenant_2')
            
            # Check that FECFile was created
            assert FECFile.objects.count() == 1
            fec_file = FECFile.objects.first()
            assert fec_file.original_filename == "test_fec.txt"
            
            # Since celery eager is true, the processing might happen immediately.
            # We test that the file is removed from disk after parsing
            if fec_file.storage_path:
                assert not os.path.exists(fec_file.storage_path)
