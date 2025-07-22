import unittest
from unittest.mock import MagicMock
from services.constraint_builder import ConstraintBuilder
from core.dto import DTOBundle

class TestConstraintBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = ConstraintBuilder()

    def test_build_payload_monobrand(self):
        bundle = MagicMock(spec=DTOBundle)
        bundle.market.mode = 'Monobrand'
        bundle.market.brands = ['BRAND1']
        bundle.capacity.channels = ['F2F']
        bundle.cycle.months = 1
        bundle.cycle.start = '2024-01-01'
        bundle.cycle.name = 'C1 2024'
        bundle.reference.months = 1
        bundle.reference.start = '2023-01-01'
        bundle.capacity.daily_capacity = {'F2F': 10}
        bundle.capacity.e_consent_rte = True
        bundle.capacity.non_prescriber_included = False
        bundle.envelopes_hist = []
        bundle.envelopes_seg = []
        bundle.non_prescriber = []
        payload = self.builder.build(bundle)
        self.assertIn('country_code', payload)
        self.assertIn('brand', payload)
        self.assertIn('constraints', payload)

    def test_build_payload_multibrand(self):
        bundle = MagicMock(spec=DTOBundle)
        bundle.market.mode = 'Multibrand'
        bundle.market.brands = ['BRAND1', 'BRAND2']
        bundle.market.specialties = {'BRAND1 and BRAND2': 'Cardiology'}
        bundle.capacity.channels = ['F2F', 'Remote']
        bundle.cycle.months = 2
        bundle.cycle.start = '2024-01-01'
        bundle.cycle.name = 'C1 2024'
        bundle.reference.months = 2
        bundle.reference.start = '2023-01-01'
        bundle.capacity.daily_capacity = {'F2F': 10, 'Remote': 5}
        bundle.capacity.e_consent_rte = False
        bundle.capacity.non_prescriber_included = False
        bundle.distribution = MagicMock()
        bundle.distribution.ratios = {'BRAND1': 60, 'BRAND2': 40}
        bundle.envelopes_hist = []
        bundle.envelopes_seg = []
        bundle.non_prescriber = []
        payload = self.builder.build(bundle)
        self.assertIn('brand', payload)
        self.assertIn('constraints', payload)
        self.assertTrue(payload['multibrand_data'])

    def test_build_payload_non_prescriber(self):
        bundle = MagicMock(spec=DTOBundle)
        bundle.market.mode = 'Monobrand'
        bundle.market.brands = ['BRAND1']
        bundle.capacity.channels = ['F2F']
        bundle.cycle.months = 1
        bundle.cycle.start = '2024-01-01'
        bundle.cycle.name = 'C1 2024'
        bundle.reference.months = 1
        bundle.reference.start = '2023-01-01'
        bundle.capacity.daily_capacity = {'F2F': 10}
        bundle.capacity.e_consent_rte = True
        bundle.capacity.non_prescriber_included = True
        bundle.capacity.non_prescriber_priority = 'High'
        bundle.envelopes_hist = []
        bundle.envelopes_seg = []
        bundle.non_prescriber = [MagicMock(channel='F2F', rule=MagicMock(min_val=1, max_val=2))]
        payload = self.builder.build(bundle)
        self.assertIn('NON_PRESCRIBERS_ENVELOPE_RULES', payload)

    def test_edge_cases(self):
        bundle = MagicMock(spec=DTOBundle)
        bundle.market.mode = 'Monobrand'
        bundle.market.brands = []
        bundle.capacity.channels = []
        bundle.cycle.months = 0
        bundle.cycle.start = ''
        bundle.cycle.name = ''
        bundle.reference.months = 0
        bundle.reference.start = ''
        bundle.capacity.daily_capacity = {}
        bundle.capacity.e_consent_rte = False
        bundle.capacity.non_prescriber_included = False
        bundle.envelopes_hist = []
        bundle.envelopes_seg = []
        bundle.non_prescriber = []
        payload = self.builder.build(bundle)
        self.assertIsInstance(payload, dict)

if __name__ == '__main__':
    unittest.main() 