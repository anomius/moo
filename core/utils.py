"""Utility classes and functions for the OCCP application."""

from typing import List, Dict, Tuple
from datetime import date
import pandas as pd
from dateutil import relativedelta

class ChannelMapper:
    """Maps channel names to canonical forms."""
    
    _map = {
        "F2F": "FACE_TO_FACE",
        "REMOTE": "REMOTE_MEETING", 
        "WHATSAPP/INSTANT MESSAGE": "WHATSAPP",
        "RTE-OPEN": "TRIGGERED_EMAIL",
        "RTE-SENT": "TRIGGERED EMAIL",
    }
    
    @classmethod
    def canonical(cls, channel: str) -> str:
        """Convert channel name to canonical form."""
        return cls._map.get(channel.upper(), channel.upper())
    
    @classmethod
    def map_all(cls, channels: List[str]) -> List[str]:
        """Map all channels in a list to canonical forms."""
        return [cls.canonical(ch) for ch in channels]

class MonthPlanner:
    """Utility for planning months and date ranges."""
    
    @staticmethod
    def get_months_to_optimize(start_date: date, months: int) -> List[str]:
        """Get list of months to optimize in YYYY-MM-DD format."""
        return [
            (start_date + relativedelta.relativedelta(months=i)).strftime("%Y-%m-%d")
            for i in range(months)
        ]
    
    @staticmethod
    def get_actual_months(ref_start_date: date, ref_months: int) -> List[str]:
        """Get list of actual months in YYYY-MM-DD format."""
        return [
            (ref_start_date + relativedelta.relativedelta(months=i)).strftime("%Y-%m-%d")
            for i in range(ref_months)
        ]

class BrandCombinator:
    """Utility for generating brand combinations."""
    
    @staticmethod
    def get_combinations(brands: List[str]) -> List[Tuple[str, ...]]:
        """Get all possible brand combinations for multibrand interactions."""
        from itertools import combinations
        return [
            combo
            for r in range(2, len(brands) + 1)
            for combo in combinations(brands, r)
        ]

class CountryCodeMapper:
    """Maps country names to country codes."""
    
    _country_codes = {
        "ARGENTINA": "AR",
        "SPAIN": "ES", 
        "SOUTH KOREA": "KR",
        "BRAZIL": "BR",
        "NETHERLANDS": "NL",
        "TURKEY": "TR",
        "JAPAN": "JP",
        "SAUDI ARABIA": "GC",
        "FRANCE": "FR",
        "ITALY": "IT",
        "BELGIUM": "BE",
        "GERMANY": "DE",
        "SWEDEN": "SE",
        "POLAND": "PL",
        "MEXICO": "MX",
        "AUSTRALIA": "AU",
        "CANADA": "CA",
        "COLOMBIA": "CO",
        "UAE": "UAE",
    }
    
    @classmethod
    def get_code(cls, country: str) -> str:
        """Get country code for given country name."""
        return cls._country_codes.get(country.upper(), "") 