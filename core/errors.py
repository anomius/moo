"""Core error classes for the OCCP application."""

class OCCPError(Exception):
    """Base exception for all OCCP-related errors."""
    pass

class ValidationError(OCCPError):
    """Raised when data validation fails."""
    pass

class RepositoryError(OCCPError):
    """Raised when database operations fail."""
    pass

class ExternalServiceError(OCCPError):
    """Raised when external service calls fail."""
    pass

class ConfigurationError(OCCPError):
    """Raised when configuration is invalid or missing."""
    pass 