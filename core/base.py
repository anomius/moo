"""Abstract base classes and interfaces for the OCCP application."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from core.dto import DTOBundle

class Repository(ABC):
    """Abstract base class for data repositories."""
    
    @abstractmethod
    def fetch_team_data(self) -> tuple:
        """Fetch team and brand data."""
        pass
    
    @abstractmethod
    def fetch_channel_data(self) -> Any:
        """Fetch channel data."""
        pass
    
    @abstractmethod
    def fetch_master_and_time_dim_data(self) -> tuple:
        """Fetch master and time dimension data."""
        pass
    
    @abstractmethod
    def fetch_validate_data(self) -> tuple:
        """Fetch validation data."""
        pass

class EmailSender(ABC):
    """Abstract base class for email services."""
    
    @abstractmethod
    def send(self, subject: str, body: str, recipients: List[str], 
             attachment_bytes: bytes, filename: str) -> None:
        """Send email with attachment."""
        pass

class ExcelExporter(ABC):
    """Abstract base class for Excel export services."""
    
    @abstractmethod
    def build(self, bundle: DTOBundle) -> bytes:
        """Build Excel workbook from DTO bundle."""
        pass

class PayloadClient(ABC):
    """Abstract base class for API payload clients."""
    
    @abstractmethod
    def post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Post payload to external API."""
        pass

class PageForm(ABC):
    """Abstract base class for Streamlit page forms."""
    
    @abstractmethod
    def render(self, *args, **kwargs):
        """Render the form UI and return DTOs."""
        pass 