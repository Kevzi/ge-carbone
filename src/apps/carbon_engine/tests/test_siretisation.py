import pytest
from decimal import Decimal
from unittest.mock import MagicMock, patch
from apps.carbon_engine.services.siretisation import SiretisationService
from apps.carbon_engine.services.calculator import CarbonCalculator
from apps.fec_parser.services import FECRow

class TestSiretisationService:
    
    @patch('apps.carbon_engine.services.siretisation.SireneStock.objects')
    def test_find_nafs_batch(self, mock_objects):
        # Mock the chained ORM calls
        mock_annotate = MagicMock()
        mock_filter = MagicMock()
        mock_order = MagicMock()
        mock_first = MagicMock()
        
        mock_objects.annotate.return_value = mock_annotate
        mock_annotate.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order
        
        # Setup mock to return a result for EDF, None for others
        class MockMatch:
            naf_code = "3511Z"
        
        # We need side_effect to return MockMatch when "EDF" is queried
        def first_side_effect(*args, **kwargs):
            return MockMatch()
            
        mock_order.first.side_effect = first_side_effect
        
        service = SiretisationService(threshold=0.3)
        noms = ["EDF ELECTRICITE DE FRANCE"]
        results = service.find_nafs_batch(noms)
        
        assert results.get("EDF ELECTRICITE DE FRANCE") == "3511Z"

from apps.carbon_engine.tests import create_fec_row

class TestCalculatorSiretisationIntegration:

    @patch('apps.carbon_engine.services.siretisation.SiretisationService.find_nafs_batch')
    def test_calculator_integration(self, mock_find_nafs):
        # Mock find_nafs_batch to return NAF for SNCF
        mock_find_nafs.return_value = {"SNCF VOYAGEURS": "4910Z"}
        
        calc = CarbonCalculator()
        
        row1 = create_fec_row(
            compte_num="624000",
            ecriture_lib="Billet train",
            debit=Decimal("100.0"),
            credit=Decimal("0.0"),
            line_number=1
        )
        row1.comp_aux_lib = "SNCF VOYAGEURS"
        row1.ecriture_date = None
        
        row2 = create_fec_row(
            compte_num="615000",
            ecriture_lib="Entretien divers",
            debit=Decimal("50.0"),
            credit=Decimal("0.0"),
            line_number=2
        )
        row2.comp_aux_lib = "SNCF VOYAGEURS"
        row2.ecriture_date = None
        
        results = calc.calculate_batch([row1, row2])
        
        # Row 1 should be NLP (train) -> Priority over NAF
        assert results[0].mapping_method == "nlp"
        assert results[0].emission_factor_name == "Transport ferroviaire"
        
        # Row 2 should be NAF
        assert results[1].mapping_method == "naf"
        assert results[1].emission_factor_name == "Transport terrestre"
        assert results[1].fournisseur_naf == "4910Z"

