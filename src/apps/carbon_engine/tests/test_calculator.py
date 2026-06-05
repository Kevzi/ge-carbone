import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import MagicMock
from apps.carbon_engine.services.calculator import CarbonCalculator, PCGMappingService
from apps.fec_parser.services import FECRow

def create_fec_row(compte_num: str, ecriture_lib: str = 'Test', debit: Decimal = Decimal('100'), credit: Decimal = Decimal('0'), line_number: int = 1) -> FECRow:
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

class TestScopeClassification:
    def test_scope_classification(self):
        calc = CarbonCalculator()
        calc.siretisation_service.get_ademe_category_for_naf = MagicMock(return_value=None)
        
        # Test Scope 1 (6062 Carburants)
        row = create_fec_row(line_number=1, compte_num="606200", ecriture_lib="Essence", debit=Decimal('100'), credit=Decimal('0'))
        result = calc.calculate_row(row)
        assert result.scope == 1
        
        # Test Scope 1 (6061 Gaz) - Use NLP to trigger Gaz factor
        row = create_fec_row(line_number=2, compte_num="606100", ecriture_lib="Achat Gaz", debit=Decimal('100'), credit=Decimal('0'))
        result = calc.calculate_row(row)
        assert result.scope == 1
        
        # Test Scope 2 (6061 Electricite) - Use NLP to trigger Electricite
        row = create_fec_row(line_number=3, compte_num="606100", ecriture_lib="Facture EDF", debit=Decimal('100'), credit=Decimal('0'))
        result = calc.calculate_row(row)
        assert result.scope == 2
        
        # Test Scope 3 (601)
        row = create_fec_row(line_number=4, compte_num="601000", ecriture_lib="Achats matieres", debit=Decimal('100'), credit=Decimal('0'))
        result = calc.calculate_row(row)
        assert result.scope == 3

class TestMappingPriority:
    def test_mapping_priority(self):
        calc = CarbonCalculator()
        calc.siretisation_service.get_ademe_category_for_naf = MagicMock(return_value='Prestation informatique')
        
        # Try a code without NLP match, it should fallback or use NAF
        factor, method, dqr = calc.mapping_service.get_emission_factor("604000", "Billet de train SNCF", fournisseur_naf="6201Z")
        assert method == 'nlp'
        assert dqr == 2
        
        factor, method, dqr = calc.mapping_service.get_emission_factor("604000", "Prestation lambda", fournisseur_naf="6201Z")
        assert method == 'naf'
        assert dqr == 3

