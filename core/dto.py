from __future__ import annotations
from typing import Literal, List, Dict, Tuple, Optional
from datetime import date
from pydantic import BaseModel, Field, PositiveInt, conint, conlist, validator, field_validator

Channel = Literal[
    "F2F", "Remote", "Phone", "Meetings", "Virtual Meetings",
    "Whatsapp/Instant Message", "RTE-Open", "RTE-Sent"
]

class BrandDTO(BaseModel, frozen=True):
    name: str
    brand_code: str
    indications: List[str] = Field(default_factory=list)
    brand_id: str

    @property
    def display_name(self) -> str:
        """Return a user-friendly display name."""
        return f"{self.name} ({self.brand_code})"

    def has_indication(self, indication: str) -> bool:
        """Check if the brand has a specific indication."""
        return indication in self.indications

class CountryBrandDTO(BaseModel, frozen=True):
    country: str                                 # Italy
    country_code: str                            # IT
    sales_line: str                              # IT_Diab_PM
    brands: conlist(BrandDTO, min_length=1)      # List of BrandDTOs
    mode: Literal["Monobrand", "Multibrand"]     # drives UI flow
    specialties: Dict[str, str] | None = None    # "BrandA and BrandB":"Cardiology"

    @property
    def brand_names(self) -> List[str]:
        return [b.name for b in self.brands]

    @property
    def brand_codes(self) -> List[str]:
        return [b.brand_code for b in self.brands]

    def get_brand_by_code(self, code: str) -> Optional[BrandDTO]:
        for b in self.brands:
            if b.brand_code == code:
                return b
        return None

    def get_brand_by_id(self, brand_id: str) -> Optional[BrandDTO]:
        for b in self.brands:
            if b.brand_id == brand_id:
                return b
        return None

    def has_brand(self, name: str) -> bool:
        return any(b.name == name for b in self.brands)

    def get_indications(self) -> List[str]:
        """Get all unique indications across brands."""
        return list({ind for b in self.brands for ind in b.indications})

class CycleDTO(BaseModel, frozen=True):
    name: str                      # "C1 2026"
    start: date
    end: date
    months: PositiveInt            # 1-12
    working_days: PositiveInt

class ReferenceCycleDTO(BaseModel, frozen=True):
    start: date
    end: date
    months: PositiveInt
    working_days: PositiveInt

class BrandDistributionDTO(BaseModel, frozen=True):
    ratios: Dict[str, conint(ge=0, le=100)]      # {brand.name: percent}
    @field_validator("ratios", mode="after")
    def _sum_to_100(cls, v):
        if sum(v.values()) != 100:
            raise ValueError("brand ratios must sum to 100 %")
        return v

class ChannelCapacityDTO(BaseModel, frozen=True):
    channels: List[Channel]
    multibrand_channels: List[Channel] = Field(default_factory=list)
    daily_capacity: Dict[Channel, float]         # per-rep per-day
    non_prescriber_included: bool
    non_prescriber_priority: Literal["Low", "Medium", "High"] | None = None
    e_consent_rte: bool

class HCPEnvelopeRule(BaseModel, frozen=True):
    min_val: int = Field(ge=0)
    max_val: int = Field(ge=0)
    @validator("max_val")
    def _max_ge_min(cls, v, values):
        if "min_val" in values and v < values["min_val"]:
            raise ValueError("max_val must be ≥ min_val")
        return v

class HistoricalEnvelopeDTO(BaseModel, frozen=True):
    channel: Channel
    reference_cycle_actual: int
    rule: HCPEnvelopeRule

class SegmentEnvelopeDTO(BaseModel, frozen=True):
    channel: Channel
    brand: str
    segment: str
    rule: HCPEnvelopeRule

class NonPrescriberEnvelopeDTO(BaseModel, frozen=True):
    channel: Channel
    rule: HCPEnvelopeRule
    
class DTOBundle(BaseModel, frozen=True):
    market: CountryBrandDTO
    cycle: CycleDTO
    reference: ReferenceCycleDTO
    distribution: BrandDistributionDTO | None   # None for monobrand
    capacity: ChannelCapacityDTO
    envelopes_hist: List[HistoricalEnvelopeDTO] | None = None
    envelopes_seg: List[SegmentEnvelopeDTO] | None = None
    non_prescriber: List[NonPrescriberEnvelopeDTO] | None = None

    @property
    def uses_segment_matrix(self) -> bool:
        return self.envelopes_seg is not None

    @property
    def is_multibrand(self) -> bool:
        return self.market.mode == "Multibrand"

    @property
    def brand_names(self) -> List[str]:
        return self.market.brand_names

    @property
    def main_brand(self) -> BrandDTO:
        """Return the first brand (for monobrand flows)."""
        return self.market.brands[0]

    def get_all_indications(self) -> List[str]:
        return self.market.get_indications()