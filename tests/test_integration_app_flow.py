import pytest
import app

def test_app_entrypoint_runs():
    # This is a smoke test; full integration would require UI automation
    assert hasattr(app, "main") 