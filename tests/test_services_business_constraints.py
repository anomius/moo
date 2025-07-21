import pytest
from services.business_constraints_service import BusinessConstraintsService

def test_validate_brand_distribution_valid():
    BusinessConstraintsService.validate_brand_distribution({"A": 60, "B": 40})

def test_validate_brand_distribution_invalid():
    with pytest.raises(ValueError):
        BusinessConstraintsService.validate_brand_distribution({"A": 70, "B": 20})
    with pytest.raises(ValueError):
        BusinessConstraintsService.validate_brand_distribution({"A": -10, "B": 110})

def test_validate_envelope_matrix_valid():
    class Dummy:
        def __init__(self, min_val, max_val):
            self.rule = type("Rule", (), {"min_val": min_val, "max_val": max_val})()
    BusinessConstraintsService.validate_envelope_matrix([Dummy(1, 2), Dummy(0, 0)])

def test_validate_envelope_matrix_invalid():
    class Dummy:
        def __init__(self, min_val, max_val):
            self.rule = type("Rule", (), {"min_val": min_val, "max_val": max_val})()
    with pytest.raises(ValueError):
        BusinessConstraintsService.validate_envelope_matrix([Dummy(2, 1)])
    with pytest.raises(ValueError):
        BusinessConstraintsService.validate_envelope_matrix([Dummy(-1, 2)])

def test_validate_channel_capacity_valid():
    BusinessConstraintsService.validate_channel_capacity({"A": 1.0, "B": 0.0})

def test_validate_channel_capacity_invalid():
    with pytest.raises(ValueError):
        BusinessConstraintsService.validate_channel_capacity({"A": -1.0}) 