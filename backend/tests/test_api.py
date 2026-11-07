from app.main import app
from app.schemas.waste_event import MaterialCategory
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "EPA WARM" in data["engine"]


def test_get_warm_factors():
    response = client.get("/api/warm/factors")
    assert response.status_code == 200
    factors = response.json()
    assert MaterialCategory.ALUMINUM_CAN.value in factors
    assert (
        factors[MaterialCategory.ALUMINUM_CAN.value]["net_avoided_co2e_per_kg"] == 9.15
    )


def test_calculate_item_endpoint():
    payload = {"category": MaterialCategory.ALUMINUM_CAN.value, "count": 5}
    response = client.post("/api/warm/calculate-item", json=payload)
    assert response.status_code == 200
    data = response.json()
    # 5 cans = 5 * 14.2g = 71g = 0.071 kg
    assert data["mass_grams"] == 71.0
    expected_co2e = round(0.071 * 9.15, 4)
    assert data["avoided_co2e_kg"] == expected_co2e


def test_calculate_item_zero_count_raises_400():
    payload = {"category": MaterialCategory.PET_PLASTIC.value, "count": 0}
    response = client.post("/api/warm/calculate-item", json=payload)
    assert response.status_code == 400
