import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from django.utils import timezone

from apps.carbon_engine.models import EmissionFactor
from apps.carbon_engine.services.ademe import ADEMESync, ADEMEAPIError
from django_tenants.utils import tenant_context
from apps.core.models import Cabinet, Domain

pytestmark = pytest.mark.django_db

@pytest.fixture
def tenant():
    tenant = Cabinet.objects.create(
        schema_name='test_tenant',
        name='Test Cabinet',
        siret='12345678901234',
        plan='starter'
    )
    Domain.objects.create(
        domain='test.localhost',
        tenant=tenant,
        is_primary=True
    )
    return tenant

@patch('apps.carbon_engine.services.ademe.requests.get')
def test_sync_factors_success(mock_get, tenant):
    service = ADEMESync()
    
    # Mocking the ADEME API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "identifiant": "12345",
                "nom_base_francais": "Electricité - mix moyen",
                "categorie": "2. Emissions indirectes liées à l'énergie",
                "sous_categorie": "Electricité",
                "valeur": 0.05,
                "unite": "kWh",
                "incertitude": 10,
                "date_creation": "2023-01-01"
            },
            {
                "identifiant": "67890",
                "nom_base_francais": "Achats de services",
                "categorie": "3. Achats de biens et services",
                "sous_categorie": "Services",
                "valeur": 1.2,
                "unite": "€",
                "incertitude": 50,
                "date_creation": "2023-02-01"
            },
            {
                "identifiant": "11111",
                "nom_base_francais": "Gaz naturel",
                "categorie": "1. Emissions directes de GES",
                "sous_categorie": "Combustibles",
                "valeur": 0.2,
                "unite": "kWh",
                "incertitude": 5,
                "date_creation": "2023-03-01"
            }
        ],
        "next": None
    }
    mock_get.return_value = mock_response
    
    snapshot_version = "2026-Q1-SNAPSHOT"
    
    with tenant_context(tenant):
        count = service.sync_factors(version=snapshot_version)
        
        assert count == 3
        
        factors = EmissionFactor.objects.filter(version=snapshot_version)
        assert factors.count() == 3
        
        electricite = factors.get(ademe_id="12345")
        assert electricite.name == "Electricité - mix moyen"
        assert electricite.category == "2. Emissions indirectes liées à l'énergie"
        assert electricite.value_kg_co2_per_unit == Decimal("0.05")
        assert electricite.version == snapshot_version
        assert electricite.scope == 2
        
        services = factors.get(ademe_id="67890")
        assert services.name == "Achats de services"
        assert services.category == "3. Achats de biens et services"
        assert services.value_kg_co2_per_euro == Decimal("1.2")
        assert services.version == snapshot_version
        assert services.scope == 3
        
        gaz = factors.get(ademe_id="11111")
        assert gaz.name == "Gaz naturel"
        assert gaz.category == "1. Emissions directes de GES"
        assert gaz.value_kg_co2_per_unit == Decimal("0.2")
        assert gaz.version == snapshot_version
        assert gaz.scope == 1

@patch('apps.carbon_engine.services.ademe.requests.get')
def test_sync_factors_api_error(mock_get, tenant):
    service = ADEMESync()
    mock_get.side_effect = Exception("API Timeout")
    
    with tenant_context(tenant):
        with pytest.raises(ADEMEAPIError):
            service.sync_factors(version="2026-Q1-SNAPSHOT")

@patch('apps.carbon_engine.services.ademe.requests.get')
def test_sync_factors_data_cleaning_aviation(mock_get, tenant):
    service = ADEMESync()
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "results": [
            {
                "identifiant": "1",
                "nom_base_francais": "Avion - passagers - moyen-courrier",
                "categorie": "Transport",
                "valeur": 0.15,
                "unite": "passager.km"
            },
            {
                "identifiant": "2",
                "nom_base_francais": "Avion - passagers - long-courrier",
                "categorie": "Transport",
                "valeur": 0.25,
                "unite": "passager.km"
            }
        ],
        "next": None
    }
    mock_get.return_value = mock_response
    
    with tenant_context(tenant):
        service.sync_factors(version="23.10")
        
        # Test that 'moyen-courrier' was replaced by 'long-courrier'
        factor_1 = EmissionFactor.objects.get(ademe_id="1")
        assert "long-courrier" in factor_1.name
        
        factor_2 = EmissionFactor.objects.get(ademe_id="2")
        assert "moyen-courrier" in factor_2.name

@patch('apps.carbon_engine.services.ademe.requests.get')
def test_sync_factors_archives_old_versions(mock_get, tenant):
    service = ADEMESync()
    
    with tenant_context(tenant):
        # Create an old factor
        EmissionFactor.objects.create(
            ademe_id="100",
            version="old-version",
            name="Old factor",
            category="Test",
            value_kg_co2_per_euro=Decimal("1.0"),
            valid_from=timezone.now().date(),
            scope=3,
            is_archived=False
        )
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "identifiant": "100",
                    "nom_base_francais": "New factor",
                    "categorie": "Test",
                    "valeur": 2.0,
                    "unite": "€"
                }
            ],
            "next": None
        }
        mock_get.return_value = mock_response
        
        service.sync_factors(version="new-version")
        
        # Verify old factor is archived
        old_factor = EmissionFactor.objects.get(version="old-version")
        assert old_factor.is_archived is True
        
        # Verify new factor is active
        new_factor = EmissionFactor.objects.get(version="new-version")
        assert new_factor.is_archived is False
