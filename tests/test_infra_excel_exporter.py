import unittest
from unittest.mock import MagicMock, patch
from infra.excel_exporter import ExcelExporterService
from core.dto import DTOBundle
from core.errors import ExternalServiceError

class TestExcelExporterService(unittest.TestCase):
    def setUp(self):
        self.exporter = ExcelExporterService()

    def test_build_success(self):
        bundle = MagicMock(spec=DTOBundle)
        # Patch _build_excel_data to avoid openpyxl logic
        with patch.object(self.exporter, '_build_excel_data', return_value=[['A', 'B', 'C']]):
            with patch.object(self.exporter, '_add_envelope_matrix_sections'):
                result = self.exporter.build(bundle)
                self.assertIsInstance(result, bytes)

    def test_build_failure(self):
        bundle = MagicMock(spec=DTOBundle)
        with patch.object(self.exporter, '_build_excel_data', side_effect=Exception('fail')):
            with self.assertRaises(ExternalServiceError):
                self.exporter.build(bundle)

if __name__ == '__main__':
    unittest.main() 