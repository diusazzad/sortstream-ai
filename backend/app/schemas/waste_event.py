from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class MaterialCategory(str, Enum):
    ALUMINUM_CAN = "aluminum_can"
    PET_PLASTIC = "pet_plastic"
    HDPE_PLASTIC = "hdpe_plastic"
    CORRUGATED_CARDBOARD = "corrugated_cardboard"
    E_WASTE = "e_waste"
    UNKNOWN = "unknown"


def get_utc_now():
    return datetime.now(timezone.utc)


class WasteDetectionEvent(BaseModel):
    track_id: int = Field(..., description="Unique persistent ByteTrack tracking ID")
    material: MaterialCategory = Field(..., description="Classified material category")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Detection confidence score"
    )
    bounding_box: List[float] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="[x1, y1, x2, y2] normalized or pixel coords",
    )
    estimated_mass_grams: float = Field(
        ..., gt=0.0, description="Estimated unit mass in grams"
    )
    timestamp: datetime = Field(
        default_factory=get_utc_now, description="UTC event timestamp"
    )
    is_sorted: bool = Field(
        default=True, description="Whether item was diverted to recycling"
    )


class ConveyorItemSummary(BaseModel):
    track_id: int
    material: MaterialCategory
    confidence: float
    mass_grams: float
    avoided_co2e_kg: float
    energy_saved_kwh: float
