import pytest
from datetime import date
from core.dto import (
    CountryBrandDTO, CycleDTO, ReferenceCycleDTO, ChannelCapacityDTO, BrandDistributionDTO, DTOBundle, HistoricalEnvelopeDTO, HCPEnvelopeRule
)
from services.business_constraints_service import BusinessConstraintsService
from services.constraint_builder import ConstraintBuilder

@pytest.fixture
def sample_bundle():
    market = CountryBrandDTO(
        country="Italy",
        country_code="IT",
        sales_line="IT_Diab_PM",
        brands=["Lantus", "Toujeo"],
        mode="Multibrand",
        specialties={"Lantus and Toujeo": "Endocrinology"}
    )
    cycle = CycleDTO(
        name="C1 2024",
        start=date(2024, 1, 1),
        end=date(2024, 3, 31),
        months=3,
        working_days=60
    )
    reference = ReferenceCycleDTO(
        start=date(2023, 1, 1),
        end=date(2023, 3, 31),
        months=3,
        working_days=60
    )
    distribution = BrandDistributionDTO(ratios={"Lantus": 60, "Toujeo": 40})
    capacity = ChannelCapacityDTO(
        channels=["F2F", "Remote"],
        multibrand_channels=["Remote"],
        daily_capacity={"F2F": 1.0, "Remote": 2.0},
        non_prescriber_included=False,
        non_prescriber_priority=None,
        e_consent_rte=True
    )
    envelopes_hist = [
        HistoricalEnvelopeDTO(channel="F2F", reference_cycle_actual=1, rule=HCPEnvelopeRule(min_val=1, max_val=3)),
        HistoricalEnvelopeDTO(channel="Remote", reference_cycle_actual=2, rule=HCPEnvelopeRule(min_val=2, max_val=4)),
    ]
    return DTOBundle(
        market=market,
        cycle=cycle,
        reference=reference,
        distribution=distribution,
        capacity=capacity,
        envelopes_hist=envelopes_hist,
        envelopes_seg=None,
        non_prescriber=None
    )

def test_business_constraints_service_calculate(sample_bundle):
    service = BusinessConstraintsService()
    import pandas as pd
    # Simulate a DataFrame as would be produced by the UI
    df = pd.DataFrame([
        {"CHANNEL": "F2F", "REFERENCE_CYCLE_ACTUAL": 1, "MIN_VALUE": 1, "MAX_VALUE": 3},
        {"CHANNEL": "Remote", "REFERENCE_CYCLE_ACTUAL": 2, "MIN_VALUE": 2, "MAX_VALUE": 4},
    ])
    summary_df, envelope_matrix_df = service.calculate_business_constraints(sample_bundle, df)
    assert not summary_df.empty
    assert not envelope_matrix_df.empty
    assert "Constraint type" in summary_df.columns
    assert "CHANNEL" in envelope_matrix_df.columns

def test_constraint_builder_build(sample_bundle):
    builder = ConstraintBuilder()
    payload = builder.build(sample_bundle)
    assert isinstance(payload, dict)
    assert "country_code" in payload
    assert "constraints" in payload or "ENVELOPE_RULES" in payload.get("constraints", {})

def test_business_constraints_service_excel_data(sample_bundle):
    service = BusinessConstraintsService()
    data = service.build_excel_data(sample_bundle)
    assert isinstance(data, list)
    assert any("Cycle" in row for row in data) 