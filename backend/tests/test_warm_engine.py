import pytest
from app.schemas.waste_event import MaterialCategory, WasteDetectionEvent
from app.services.warm_calculator import EPA_WARM_V16_FACTORS, EpawarmAccountingEngine


@pytest.fixture
def engine():
    return EpawarmAccountingEngine()


def test_aluminum_can_offset(engine):
    """Verify Aluminum can formula: 14.2g = 0.0142 kg * 9.15 = 0.1299 kg CO2e."""
    summary = engine.calculate_single_item(MaterialCategory.ALUMINUM_CAN)
    assert summary.mass_grams == 14.2
    expected_co2e = round(0.0142 * 9.15, 4)
    assert summary.avoided_co2e_kg == expected_co2e
    assert summary.energy_saved_kwh == round(0.0142 * 14.0, 4)


def test_custom_mass_override(engine):
    """Verify that explicit mass in grams overrides default."""
    summary = engine.calculate_single_item(
        MaterialCategory.PET_PLASTIC, mass_grams=50.0
    )
    assert summary.mass_grams == 50.0
    # 50g = 0.05 kg * 1.20 = 0.06 kg CO2e
    assert summary.avoided_co2e_kg == 0.06


def test_unknown_material_zero_offset(engine):
    """Verify unknown material gracefully yields zero emission offset without throwing."""
    summary = engine.calculate_single_item(MaterialCategory.UNKNOWN)
    assert summary.avoided_co2e_kg == 0.0
    assert summary.energy_saved_kwh == 0.0


def test_empty_session_telemetry_no_division_by_zero(engine):
    """Verify zero-division safeguards when no items passed."""
    telemetry = engine.compute_session_telemetry(
        session_id="empty", events=[], elapsed_seconds=0.0
    )
    assert telemetry.items_total == 0
    assert telemetry.items_per_minute == 0.0
    assert telemetry.sorting_purity_percent == 100.0
    assert telemetry.total_mass_kg == 0.0
    assert telemetry.total_avoided_co2e_kg == 0.0


def test_multi_item_telemetry_and_purity(engine):
    """Verify multi-class aggregation and purity computation."""
    events = [
        WasteDetectionEvent(
            track_id=1,
            material=MaterialCategory.ALUMINUM_CAN,
            confidence=0.95,
            bounding_box=[10.0, 10.0, 50.0, 50.0],
            estimated_mass_grams=14.2,
            is_sorted=True,
        ),
        WasteDetectionEvent(
            track_id=2,
            material=MaterialCategory.PET_PLASTIC,
            confidence=0.91,
            bounding_box=[20.0, 20.0, 60.0, 60.0],
            estimated_mass_grams=23.8,
            is_sorted=True,
        ),
        WasteDetectionEvent(
            track_id=3,
            material=MaterialCategory.CORRUGATED_CARDBOARD,
            confidence=0.88,
            bounding_box=[30.0, 30.0, 70.0, 70.0],
            estimated_mass_grams=65.0,
            is_sorted=False,  # Rejected / Unsorted
        ),
    ]

    telemetry = engine.compute_session_telemetry(
        session_id="test-session", events=events, elapsed_seconds=60.0
    )

    assert telemetry.items_total == 3
    # 2 sorted out of 3 total = 66.67%
    assert telemetry.sorting_purity_percent == 66.67
    assert telemetry.items_per_minute == 3.0
    # Mass sorted: 14.2g (Al) + 23.8g (PET) = 38g = 0.038 kg
    assert telemetry.total_mass_kg == 0.038
    # Breakdown checks
    al_stats = telemetry.breakdown_by_material[MaterialCategory.ALUMINUM_CAN.value]
    assert al_stats.count == 1
    assert al_stats.total_mass_kg == 0.0142
