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
        
        rows = parser.parse_all(fec_content)
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
        
        chunks = list(parser.parse_streaming(content.encode('utf-8')))
        
        # Should have 3 chunks: [2, 2, 1] rows
        assert len(chunks) == 3
        assert len(chunks[0]) == 2
        assert len(chunks[1]) == 2
        assert len(chunks[2]) == 1
