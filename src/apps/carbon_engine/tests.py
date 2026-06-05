"""
Tests for Carbon Engine services.
"""
import pytest
from decimal import Decimal
from unittest.mock import MagicMock
from apps.carbon_engine.services import (
    PCGMappingService, CarbonCalculator, CarbonCalculationResult
)
from apps.fec_parser.services import FECRow
from datetime import datetime


def create_fec_row(
    compte_num: str,
    ecriture_lib: str = 'Test',
    debit: Decimal = Decimal('100'),
    credit: Decimal = Decimal('0'),
    line_number: int = 1
) -> FECRow:
    """Helper to create FECRow for testing."""
    return FECRow(
        line_number=line_number,
        journal_code='AC',
        journal_lib='Achats',
        ecriture_num='001',
        ecriture_date=datetime.now(),
        compte_num=compte_num,
        compte_lib='',
        comp_aux_num='',
        comp_aux_lib='',
        piece_ref='FA001',
        piece_date=datetime.now(),
        ecriture_lib=ecriture_lib,
        debit=debit,
        credit=credit,
        ecriture_let='',
        date_let=None,
        valid_date=datetime.now(),
        montant_devise=None,
        idevise=''
    )


class TestPCGMappingService:
    """Tests for PCGMappingService."""
    
    def test_prefix_mapping_transport(self):
        service = PCGMappingService()
        factor, method, dqr = service.get_emission_factor('624100', '')
        
        assert factor is not None
        assert factor.name == 'Transports'
        assert method == 'pcg_prefix'
        assert dqr == 3
    
    def test_prefix_mapping_services(self):
        service = PCGMappingService()
        factor, method, dqr = service.get_emission_factor('615000', '')
        
        assert factor is not None
        assert factor.name == 'Entretien réparations'
    
    def test_nlp_mapping_sncf(self):
        service = PCGMappingService()
        factor, method, dqr = service.get_emission_factor(
            '625100',
            'Billet SNCF Paris-Lyon'
        )
        
        assert factor is not None
        assert factor.name == 'Transport ferroviaire'
        assert method == 'nlp'
        assert factor.value_kg_co2_per_euro == Decimal('0.03')
    
    def test_nlp_mapping_avion(self):
        service = PCGMappingService()
        factor, method, dqr = service.get_emission_factor(
            '625100',
            'Vol Air France CDG-JFK'
        )
        
        assert factor is not None
        assert factor.name == 'Transport aérien'
        assert factor.value_kg_co2_per_euro == Decimal('0.25')
    
    def test_nlp_mapping_cloud(self):
        service = PCGMappingService()
        factor, method, dqr = service.get_emission_factor(
            '613500',
            'AWS EC2 instances'
        )
        
        assert factor is not None
        assert factor.name == 'Cloud computing'
    
    def test_fallback_unknown_account(self):
        service = PCGMappingService()
        factor, method, dqr = service.get_emission_factor('999999', '')
        
        assert factor is None
        assert method == 'fallback'
        assert dqr == 1


class TestCarbonCalculator:
    """Tests for CarbonCalculator."""
    
    def test_calculate_expense_row(self):
        calculator = CarbonCalculator()
        row = create_fec_row(
            compte_num='606100',
            ecriture_lib='Fournitures bureau',
            debit=Decimal('500'),
            credit=Decimal('0')
        )
        
        result = calculator.calculate_row(row)
        
        assert result.co2_kg > 0
        assert result.scope == 3
        assert result.mapping_method != 'excluded'
    
    def test_exclude_non_expense_account(self):
        calculator = CarbonCalculator()
        row = create_fec_row(
            compte_num='411000',  # Client account (class 4)
            ecriture_lib='Facture client',
            debit=Decimal('1000'),
            credit=Decimal('0')
        )
        
        result = calculator.calculate_row(row)
        
        assert result.co2_kg == Decimal('0')
        assert result.mapping_method == 'excluded'
    
    def test_calculate_with_nlp_boost(self):
        calculator = CarbonCalculator()
        
        # Generic transport expense
        row1 = create_fec_row(
            compte_num='625100',
            ecriture_lib='Déplacement',
            debit=Decimal('100')
        )
        
        # Specific train expense (NLP)
        row2 = create_fec_row(
            compte_num='625100',
            ecriture_lib='Billet TGV Paris-Marseille',
            debit=Decimal('100')
        )
        
        result1 = calculator.calculate_row(row1)
        result2 = calculator.calculate_row(row2)
        
        # Train should have lower emissions than generic transport
        assert result2.co2_kg < result1.co2_kg
    
    def test_aggregate_results(self):
        calculator = CarbonCalculator()
        
        rows = [
            create_fec_row('606100', 'Fournitures', Decimal('100'), line_number=1),
            create_fec_row('624100', 'Transport', Decimal('200'), line_number=2),
            create_fec_row('625100', 'Billet SNCF', Decimal('50'), line_number=3),
        ]
        
        results = calculator.calculate_batch(rows)
        totals = calculator.aggregate_results(results)
        
        assert totals['total_co2_kg'] > 0
        assert totals['total_rows'] == 3
        assert totals['scope3_co2_kg'] > 0
    
    def test_batch_calculation(self):
        calculator = CarbonCalculator()
        
        rows = [
            create_fec_row('606100', 'Item 1', Decimal('100'), line_number=i)
            for i in range(10)
        ]
        
        results = calculator.calculate_batch(rows)
        
        assert len(results) == 10
        assert all(isinstance(r, CarbonCalculationResult) for r in results)


class TestDQRScoring:
    """Tests for Data Quality Rating scoring."""
    
    def test_nlp_match_high_dqr(self):
        calculator = CarbonCalculator()
        row = create_fec_row(
            compte_num='625100',
            ecriture_lib='Billet train SNCF'
        )
        
        result = calculator.calculate_row(row)
        assert result.dqr >= 4  # NLP match = high quality
    
    def test_prefix_match_medium_dqr(self):
        calculator = CarbonCalculator()
        row = create_fec_row(
            compte_num='606100',
            ecriture_lib='Achat divers'  # No NLP match
        )
        
        result = calculator.calculate_row(row)
        assert result.dqr == 3  # Prefix match = medium quality
    
    def test_fallback_low_dqr(self):
        calculator = CarbonCalculator()
        row = create_fec_row(
            compte_num='698000',  # Unknown, will fallback
            ecriture_lib='Charge exceptionnelle'
        )
        
        result = calculator.calculate_row(row)
        # Should get fallback or low DQR
        assert result.dqr <= 3
