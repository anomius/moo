import pytest
from infra.excel_exporter import ExcelExporterService

def test_excel_exporter_instantiation():
    exporter = ExcelExporterService()
    assert exporter is not None

# Add more specific tests for build method as needed (mock DTOBundle) 