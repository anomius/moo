import pytest
from core.dto import (
    BrandDTO, CountryBrandDTO, CycleDTO, ReferenceCycleDTO, BrandDistributionDTO,
    ChannelCapacityDTO, HCPEnvelopeRule, HistoricalEnvelopeDTO, SegmentEnvelopeDTO,
    NonPrescriberEnvelopeDTO, DTOBundle
)
from datetime import date

def test_brand_dto():
    b = BrandDTO(name="BrandA", brand_code="A", brand_id="BRAND1")
    assert b.display_name == "BrandA (A)"
    assert not b.has_indication("Diabetes")

def test_country_brand_dto():
    b = BrandDTO(name="BrandA", brand_code="A", brand_id="BRAND1")
    cb = CountryBrandDTO(
        country="Italy", country_code="IT", sales_line="IT_Diab_PM",
        brands=[b], mode="Monobrand"
    )
    assert cb.brand_names == ["BrandA"]
    assert cb.brand_codes == ["A"]
    assert cb.get_brand_by_code("A") == b
    assert cb.get_brand_by_id("BRAND1") == b
    assert cb.has_brand("BrandA")
    assert cb.get_indications() == []

def test_cycle_dto():
    c = CycleDTO(name="C1 2024", start=date(2024,1,1), end=date(2024,1,31), months=1, working_days=20)
    assert c.name == "C1 2024"

def test_reference_cycle_dto():
    r = ReferenceCycleDTO(start=date(2023,1,1), end=date(2023,1,31), months=1, working_days=20)
    assert r.months == 1

def test_brand_distribution_dto_valid():
    d = BrandDistributionDTO(ratios={"BrandA": 60, "BrandB": 40})
    assert d.ratios["BrandA"] == 60

def test_brand_distribution_dto_invalid():
    with pytest.raises(ValueError):
        BrandDistributionDTO(ratios={"BrandA": 70, "BrandB": 20})

def test_channel_capacity_dto():
    c = ChannelCapacityDTO(
        channels=["F2F"],
        multibrand_channels=[],
        daily_capacity={"F2F": 5.0},
        non_prescriber_included=False,
        non_prescriber_priority=None,
        e_consent_rte=True
    )
    assert c.daily_capacity["F2F"] == 5.0

def test_hcp_envelope_rule_valid():
    rule = HCPEnvelopeRule(min_val=1, max_val=3)
    assert rule.max_val == 3

def test_hcp_envelope_rule_invalid():
    with pytest.raises(ValueError):
        HCPEnvelopeRule(min_val=4, max_val=2)

def test_historical_envelope_dto():
    rule = HCPEnvelopeRule(min_val=1, max_val=3)
    h = HistoricalEnvelopeDTO(channel="F2F", reference_cycle_actual=2, rule=rule)
    assert h.reference_cycle_actual == 2

def test_segment_envelope_dto():
    rule = HCPEnvelopeRule(min_val=1, max_val=3)
    s = SegmentEnvelopeDTO(channel="F2F", brand="BrandA", segment="A", rule=rule)
    assert s.segment == "A"

def test_non_prescriber_envelope_dto():
    rule = HCPEnvelopeRule(min_val=1, max_val=3)
    n = NonPrescriberEnvelopeDTO(channel="F2F", rule=rule)
    assert n.channel == "F2F"

def test_dto_bundle():
    b = BrandDTO(name="BrandA", brand_code="A", brand_id="BRAND1")
    cb = CountryBrandDTO(
        country="Italy", country_code="IT", sales_line="IT_Diab_PM",
        brands=[b], mode="Monobrand"
    )
    c = CycleDTO(name="C1 2024", start=date(2024,1,1), end=date(2024,1,31), months=1, working_days=20)
    r = ReferenceCycleDTO(start=date(2023,1,1), end=date(2023,1,31), months=1, working_days=20)
    cap = ChannelCapacityDTO(
        channels=["F2F"],
        multibrand_channels=[],
        daily_capacity={"F2F": 5.0},
        non_prescriber_included=False,
        non_prescriber_priority=None,
        e_consent_rte=True
    )
    bundle = DTOBundle(
        market=cb, cycle=c, reference=r, distribution=None, capacity=cap
    )
    assert bundle.market.country == "Italy" 