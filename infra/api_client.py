"""API client for OCCP optimization service."""

import json
import os
import requests
from typing import Dict, Any
from core.base import PayloadClient
from core.errors import ExternalServiceError
from core.utils import CountryCodeMapper

class ApiClient(PayloadClient):
    """Client for OCCP optimization API."""
    
    def __init__(self, base_url: str, verify_ssl: bool = True):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for the OCCP API
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url
        self.verify_ssl = verify_ssl
        self.ssl_cert_path = "/etc/ssl/certs/ca-certificates.crt" if verify_ssl else None
    
    def post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post payload to OCCP optimization API.
        
        Args:
            payload: OCCP constraint payload
            
        Returns:
            API response as dictionary
            
        Raises:
            ExternalServiceError: If API call fails
        """
        try:
            # Prepare the API payload
            api_payload = self._prepare_api_payload(payload)
            
            # Make the API call
            response = requests.post(
                self.base_url,
                data=json.dumps(api_payload),
                verify=self.ssl_cert_path if self.verify_ssl else False,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            # Check response status
            if response.status_code == 200:
                return {"status": "success", "data": response.text}
            else:
                raise ExternalServiceError(
                    f"API call failed with status {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            raise ExternalServiceError(f"Network error during API call: {e}")
        except Exception as e:
            raise ExternalServiceError(f"Unexpected error during API call: {e}")
    
    def _prepare_api_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare the API payload from the constraint payload.
        
        Args:
            payload: OCCP constraint payload
            
        Returns:
            Formatted API payload
        """
        # Extract required fields
        country_code = payload.get("country_code", "")
        brands = payload.get("brand", [])
        constraints = payload.get("constraints", {})
        
        # Resolve brand codes
        resolved_brands = self._resolve_brands(brands)
        
        # Build API payload
        api_payload = {
            "gbu": "gen",
            "countrycode": country_code,
            "brand": resolved_brands,
            "subtype": "BRICK",
            "constraints": json.dumps(payload),
        }
        
        return api_payload
    
    def _resolve_brands(self, brands: list) -> str:
        """
        Resolve brand names to their corresponding codes.
        
        Args:
            brands: List of brand names
            
        Returns:
            Underscore-separated brand codes
        """
        # This is a simplified version - in the actual implementation,
        # you would have a proper brand code mapping
        brand_codes = []
        for brand in brands:
            # Simple mapping - in reality, this would use a proper brand code service
            brand_code = brand.upper().replace(" ", "_")
            brand_codes.append(brand_code)
        
        return "_".join(brand_codes)
    
    @classmethod
    def create_for_environment(cls, environment: str = "DEV") -> "ApiClient":
        """
        Create API client for specific environment.
        
        Args:
            environment: Environment name (DEV, UAT, PROD)
            
        Returns:
            Configured API client
        """
        if environment == "PROD":
            base_url = "https://apps.factoryv2.p171649450587.aws-emea.sanofi.com/prod/turing-geneticalgorithm/trigger/run"
            verify_ssl = True
        elif environment == "UAT":
            base_url = "https://apps.factoryv2.p171649450587.aws-emea.sanofi.com/uat/turing-geneticalgorithm/trigger/run"
            verify_ssl = True
        else:  # DEV
            base_url = "http://localhost:8000/api/occp"  # Placeholder for dev
            verify_ssl = False
        
        return cls(base_url, verify_ssl) 