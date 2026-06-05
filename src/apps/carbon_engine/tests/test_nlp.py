import pytest
from decimal import Decimal
from django.utils import timezone
from apps.report_generator.models import Report
from apps.carbon_engine.models import CarbonEntry, EmissionFactor
from apps.carbon_engine.tasks import enrich_fec_nlp_task
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

@pytest.fixture
def sample_report(tenant, admin_user):
    with tenant_context(tenant):
        report = Report.objects.create(
            cabinet=tenant,
            created_by=admin_user,
            client_name="Client Test",
            fiscal_year=2024,
            status="processing",
            total_co2_kg=Decimal("0"),
            average_dqr=Decimal("0"),
            pdf_url=""
        )
        return report

@pytest.fixture
def sample_emission_factor(tenant):
    with tenant_context(tenant):
        return EmissionFactor.objects.create(
            ademe_id="test_id_1",
            name="Facteur Test",
            category="Achats de Services",
            value_kg_co2_per_euro=Decimal("1.5"),
            version="1.0",
            valid_from=timezone.now().date()
        )

@pytest.fixture
def sample_carbon_entries(tenant, sample_report, sample_emission_factor):
    with tenant_context(tenant):
        entries = []
        for i in range(5):
            entries.append(
                CarbonEntry(
                    report=sample_report,
                    fec_line_number=i+1,
                    compte_num=f"604{i}",
                    ecriture_lib="Prestation de service",
                    debit=Decimal("100"),
                    credit=Decimal("0"),
                    co2_kg=Decimal("0"),
                    mapping_method="pcg_prefix",
                    dqr=3
                )
            )
        return CarbonEntry.objects.bulk_create(entries)

from unittest.mock import patch

def test_enrich_fec_nlp_task(tenant, sample_report, sample_carbon_entries):
    """
    Test that the NLP task enriches CarbonEntries properly.
    """
    # Mock the NLPService so we don't try to load ONNX in tests
    with patch("apps.carbon_engine.tasks.NLPService") as mock_nlp:
        mock_instance = mock_nlp.return_value
        mock_instance.predict_category.return_value = ["Achats de Services" for _ in range(5)]

        # Call the task synchronously
        result = enrich_fec_nlp_task(sample_report.id, tenant.schema_name)
        
        assert result == 5
        
        # Verify entries were updated
        with tenant_context(tenant):
            entries = CarbonEntry.objects.filter(report=sample_report)
            assert entries.count() == 5
            for entry in entries:
                assert entry.mapping_method == "nlp"
                assert entry.dqr == 4
                assert entry.emission_factor is not None
                assert entry.emission_factor.category == "Achats de Services"
