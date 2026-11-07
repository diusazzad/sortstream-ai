from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .schemas.metrics import ConveyorTelemetry
from .schemas.waste_event import (
    ConveyorItemSummary,
    MaterialCategory,
    WasteDetectionEvent,
)
from .services.warm_calculator import EPA_WARM_V16_FACTORS, EpawarmAccountingEngine

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Real-time Conveyor Sorting & EPA WARM v16 Lifecycle Carbon Accounting API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

warm_engine = EpawarmAccountingEngine()


class QuickEstimateRequest(BaseModel):
    category: MaterialCategory
    mass_grams: Optional[float] = None
    count: int = 1


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "engine": "EPA WARM v16",
    }


@app.get("/api/warm/factors")
def get_warm_factors():
    """Returns official EPA WARM v16 lifecycle factors per material."""
    return {
        category.value: {
            "default_unit_mass_grams": profile.default_unit_mass_grams,
            "net_avoided_co2e_per_kg": profile.net_avoided_co2e_per_kg,
            "energy_saved_kwh_per_kg": profile.energy_saved_kwh_per_kg,
            "landfill_density_m3_per_kg": profile.landfill_density_m3_per_kg,
        }
        for category, profile in EPA_WARM_V16_FACTORS.items()
    }


@app.post("/api/warm/calculate-item", response_model=ConveyorItemSummary)
def calculate_item_offset(request: QuickEstimateRequest):
    """Calculates avoided CO2e and energy savings for detected items with zero intermediate rounding error."""
    if request.count <= 0:
        raise HTTPException(status_code=400, detail="Count must be greater than 0")

    profile = warm_engine.get_factor_profile(request.category)
    unit_mass = (
        request.mass_grams
        if (request.mass_grams is not None and request.mass_grams > 0)
        else profile.default_unit_mass_grams
    )
    total_mass_g = unit_mass * request.count
    total_mass_kg = total_mass_g / 1000.0

    total_co2e = round(total_mass_kg * profile.net_avoided_co2e_per_kg, 4)
    total_energy = round(total_mass_kg * profile.energy_saved_kwh_per_kg, 4)

    return ConveyorItemSummary(
        track_id=0,
        material=request.category,
        confidence=1.0,
        mass_grams=round(total_mass_g, 2),
        avoided_co2e_kg=total_co2e,
        energy_saved_kwh=total_energy,
    )


class BatchEventsRequest(BaseModel):
    session_id: str = "demo-conveyor-session"
    elapsed_seconds: float = 60.0
    events: List[WasteDetectionEvent]


@app.post("/api/warm/compute-telemetry", response_model=ConveyorTelemetry)
def compute_telemetry(batch: BatchEventsRequest):
    """Computes comprehensive telemetry for a list of tracked waste detection events."""
    return warm_engine.compute_session_telemetry(
        session_id=batch.session_id,
        events=batch.events,
        elapsed_seconds=batch.elapsed_seconds,
    )
