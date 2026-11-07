from typing import Dict, List

from pydantic import BaseModel, Field

from .waste_event import MaterialCategory


class MaterialImpactMetrics(BaseModel):
    category: MaterialCategory
    count: int = Field(default=0, ge=0)
    total_mass_kg: float = Field(default=0.0, ge=0.0)
    net_avoided_co2e_kg: float = Field(default=0.0)
    energy_saved_kwh: float = Field(default=0.0)
    landfill_diverted_m3: float = Field(default=0.0, ge=0.0)


class ConveyorTelemetry(BaseModel):
    session_id: str
    items_total: int = Field(default=0, ge=0)
    items_per_minute: float = Field(default=0.0, ge=0.0)
    sorting_purity_percent: float = Field(default=100.0, ge=0.0, le=100.0)
    total_mass_kg: float = Field(default=0.0, ge=0.0)
    total_avoided_co2e_kg: float = Field(default=0.0)
    total_avoided_co2e_metric_tons: float = Field(default=0.0)
    total_energy_saved_kwh: float = Field(default=0.0)
    total_energy_saved_million_btu: float = Field(default=0.0)
    landfill_volume_diverted_m3: float = Field(default=0.0, ge=0.0)
    breakdown_by_material: Dict[str, MaterialImpactMetrics] = Field(
        default_factory=dict
    )
