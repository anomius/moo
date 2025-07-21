import pytest
from infra.email_service import EmailService

def test_email_service_instantiation():
    service = EmailService()
    assert service is not None

# Add more specific tests for email sending logic as needed (mock dependencies) 