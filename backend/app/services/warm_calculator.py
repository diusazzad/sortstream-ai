"""
EPA WARM v16 (Waste Reduction Model) Carbon & Energy Accounting Engine.
Implements life-cycle greenhouse gas (GHG) and energy offsets for municipal
and industrial recyclables based on U.S. Environmental Protection Agency data.

Mathematical Formulation:
    Delta_E_net = sum_m [ M_m * (EF_landfill,m - EF_recycle,m) ]
    where:
        M_m = Mass of material m in kg or metric tons
        EF_landfill,m = Baseline landfill emissions factor (kg CO2e / kg)
        EF_recycle,m = Alternative recycling emissions factor (kg CO2e / kg)
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from ..schemas.metrics import ConveyorTelemetry, MaterialImpactMetrics
from ..schemas.waste_event import (
    ConveyorItemSummary,
    MaterialCategory,
    WasteDetectionEvent,
)


@dataclass(frozen=True)
class MaterialFactorProfile:
    category: MaterialCategory
    default_unit_mass_grams: float
    landfill_factor_kg_co2e_per_kg: float
    recycle_factor_kg_co2e_per_kg: float
    energy_saved_kwh_per_kg: float
    landfill_density_m3_per_kg: float

    @property
    def net_avoided_co2e_per_kg(self) -> float:
        """Net GHG savings = Baseline landfill - Recycling lifecycle footprint."""
        return self.landfill_factor_kg_co2e_per_kg - self.recycle_factor_kg_co2e_per_kg


# EPA WARM v16 Certified Life-Cycle Factors (kg CO2e and kWh per kg of material)
EPA_WARM_V16_FACTORS: Dict[MaterialCategory, MaterialFactorProfile] = {
    MaterialCategory.ALUMINUM_CAN: MaterialFactorProfile(
        category=MaterialCategory.ALUMINUM_CAN,
        default_unit_mass_grams=14.2,
        landfill_factor_kg_co2e_per_kg=0.02,
        recycle_factor_kg_co2e_per_kg=-9.13,  # Net avoided = 0.02 - (-9.13) = 9.15
        energy_saved_kwh_per_kg=14.0,
        landfill_density_m3_per_kg=0.0074,
    ),
    MaterialCategory.PET_PLASTIC: MaterialFactorProfile(
        category=MaterialCategory.PET_PLASTIC,
        default_unit_mass_grams=23.8,
        landfill_factor_kg_co2e_per_kg=0.04,
        recycle_factor_kg_co2e_per_kg=-1.16,  # Net avoided = 1.20
        energy_saved_kwh_per_kg=6.1,
        landfill_density_m3_per_kg=0.0035,
    ),
    MaterialCategory.HDPE_PLASTIC: MaterialFactorProfile(
        category=MaterialCategory.HDPE_PLASTIC,
        default_unit_mass_grams=35.0,
        landfill_factor_kg_co2e_per_kg=0.04,
        recycle_factor_kg_co2e_per_kg=-0.92,  # Net avoided = 0.96
        energy_saved_kwh_per_kg=5.4,
        landfill_density_m3_per_kg=0.0038,
    ),
    MaterialCategory.CORRUGATED_CARDBOARD: MaterialFactorProfile(
        category=MaterialCategory.CORRUGATED_CARDBOARD,
        default_unit_mass_grams=65.0,
        landfill_factor_kg_co2e_per_kg=0.23,
        recycle_factor_kg_co2e_per_kg=-3.11,  # Net avoided = 3.34
        energy_saved_kwh_per_kg=3.9,
        landfill_density_m3_per_kg=0.0042,
    ),
    MaterialCategory.E_WASTE: MaterialFactorProfile(
        category=MaterialCategory.E_WASTE,
        default_unit_mass_grams=80.0,
        landfill_factor_kg_co2e_per_kg=0.05,
        recycle_factor_kg_co2e_per_kg=-1.85,  # Net avoided = 1.90
        energy_saved_kwh_per_kg=7.2,
        landfill_density_m3_per_kg=0.0025,
    ),
    MaterialCategory.UNKNOWN: MaterialFactorProfile(
        category=MaterialCategory.UNKNOWN,
        default_unit_mass_grams=30.0,
        landfill_factor_kg_co2e_per_kg=0.0,
        recycle_factor_kg_co2e_per_kg=0.0,
        energy_saved_kwh_per_kg=0.0,
        landfill_density_m3_per_kg=0.0030,
    ),
}

KWH_TO_MILLION_BTU = 0.003412142


class EpawarmAccountingEngine:
    """Deterministic life-cycle carbon & energy accounting engine."""

    def __init__(
        self,
        custom_factors: Optional[Dict[MaterialCategory, MaterialFactorProfile]] = None,
    ):
        self.factors = custom_factors or EPA_WARM_V16_FACTORS

    def get_factor_profile(self, category: MaterialCategory) -> MaterialFactorProfile:
        return self.factors.get(category, self.factors[MaterialCategory.UNKNOWN])

    def calculate_single_item(
        self, category: MaterialCategory, mass_grams: Optional[float] = None
    ) -> ConveyorItemSummary:
        """Calculate environmental offset for a single detected item."""
        profile = self.get_factor_profile(category)
        effective_mass_g = (
            mass_grams
            if (mass_grams is not None and mass_grams > 0)
            else profile.default_unit_mass_grams
        )
        mass_kg = effective_mass_g / 1000.0

        avoided_co2e_kg = mass_kg * profile.net_avoided_co2e_per_kg
        energy_saved_kwh = mass_kg * profile.energy_saved_kwh_per_kg

        return ConveyorItemSummary(
            track_id=0,
            material=category,
            confidence=1.0,
            mass_grams=round(effective_mass_g, 2),
            avoided_co2e_kg=round(avoided_co2e_kg, 4),
            energy_saved_kwh=round(energy_saved_kwh, 4),
        )

    def compute_session_telemetry(
        self,
        session_id: str,
        events: List[WasteDetectionEvent],
        elapsed_seconds: float = 60.0,
    ) -> ConveyorTelemetry:
        """
        Aggregate full stream telemetry and compute total avoided emissions.
        Guarantees zero-division safety and deterministic precision.
        """
        breakdown: Dict[str, MaterialImpactMetrics] = {
            cat.value: MaterialImpactMetrics(category=cat)
            for cat in MaterialCategory
            if cat != MaterialCategory.UNKNOWN
        }

        total_items = 0
        sorted_items = 0
        total_mass_kg = 0.0
        total_avoided_co2e_kg = 0.0
        total_energy_saved_kwh = 0.0
        total_landfill_m3 = 0.0

        for event in events:
            total_items += 1
            if not event.is_sorted:
                continue

            sorted_items += 1
            profile = self.get_factor_profile(event.material)
            mass_g = (
                event.estimated_mass_grams
                if event.estimated_mass_grams > 0
                else profile.default_unit_mass_grams
            )
            mass_kg = mass_g / 1000.0

            item_co2e_kg = mass_kg * profile.net_avoided_co2e_per_kg
            item_energy_kwh = mass_kg * profile.energy_saved_kwh_per_kg
            item_landfill_m3 = mass_kg * profile.landfill_density_m3_per_kg

            total_mass_kg += mass_kg
            total_avoided_co2e_kg += item_co2e_kg
            total_energy_saved_kwh += item_energy_kwh
            total_landfill_m3 += item_landfill_m3

            cat_key = event.material.value
            if cat_key in breakdown:
                entry = breakdown[cat_key]
                entry.count += 1
                entry.total_mass_kg = round(entry.total_mass_kg + mass_kg, 4)
                entry.net_avoided_co2e_kg = round(
                    entry.net_avoided_co2e_kg + item_co2e_kg, 4
                )
                entry.energy_saved_kwh = round(
                    entry.energy_saved_kwh + item_energy_kwh, 4
                )
                entry.landfill_diverted_m3 = round(
                    entry.landfill_diverted_m3 + item_landfill_m3, 6
                )

        # Throughput & purity calculations
        duration_minutes = max(elapsed_seconds, 1.0) / 60.0
        items_per_minute = round(total_items / duration_minutes, 2)
        purity_percent = (
            round((sorted_items / total_items * 100.0), 2) if total_items > 0 else 100.0
        )

        return ConveyorTelemetry(
            session_id=session_id,
            items_total=total_items,
            items_per_minute=items_per_minute,
            sorting_purity_percent=purity_percent,
            total_mass_kg=round(total_mass_kg, 4),
            total_avoided_co2e_kg=round(total_avoided_co2e_kg, 4),
            total_avoided_co2e_metric_tons=round(total_avoided_co2e_kg / 1000.0, 6),
            total_energy_saved_kwh=round(total_energy_saved_kwh, 4),
            total_energy_saved_million_btu=round(
                total_energy_saved_kwh * KWH_TO_MILLION_BTU, 4
            ),
            landfill_volume_diverted_m3=round(total_landfill_m3, 6),
            breakdown_by_material=breakdown,
        )
