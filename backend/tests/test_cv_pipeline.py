import pytest
from app.core.detector import SyntheticConveyorGenerator, WasteDetector
from app.core.tracker import ConveyorTripwireTracker, calculate_iou
from app.main import app
from app.schemas.waste_event import MaterialCategory
from fastapi.testclient import TestClient

client = TestClient(app)


def test_iou_calculation():
    # Exact overlap
    box = [10.0, 10.0, 50.0, 50.0]
    assert calculate_iou(box, box) == 1.0

    # No overlap
    boxA = [0.0, 0.0, 10.0, 10.0]
    boxB = [20.0, 20.0, 30.0, 30.0]
    assert calculate_iou(boxA, boxB) == 0.0

    # Partial overlap
    box1 = [0.0, 0.0, 20.0, 20.0]  # area 400
    box2 = [10.0, 0.0, 30.0, 20.0]  # area 400, intersection [10, 0, 20, 20] area 200
    # union = 400 + 400 - 200 = 600, IoU = 200 / 600 = 1/3
    assert abs(calculate_iou(box1, box2) - (1.0 / 3.0)) < 1e-4


def test_tripwire_exact_single_count_guarantee():
    """Verify that an object crossing the tripwire boundary triggers exactly once."""
    tracker = ConveyorTripwireTracker(
        tripwire_y=200.0, tripwire_direction="top_to_bottom"
    )

    # Frame 1: Object above tripwire line (y: 100 to 180, cy = 140)
    det_f1 = [
        {
            "bbox": [50.0, 100.0, 90.0, 180.0],
            "material": MaterialCategory.ALUMINUM_CAN,
            "confidence": 0.95,
            "mass_grams": 14.2,
        }
    ]
    tracks_f1, events_f1 = tracker.update(det_f1)
    assert len(tracks_f1) == 1
    assert len(events_f1) == 0  # not yet crossed
    track_id = tracks_f1[0].track_id

    # Frame 2: Object moves across tripwire line (y: 180 to 260, cy = 220)
    det_f2 = [
        {
            "bbox": [52.0, 180.0, 92.0, 260.0],
            "material": MaterialCategory.ALUMINUM_CAN,
            "confidence": 0.96,
            "mass_grams": 14.2,
        }
    ]
    tracks_f2, events_f2 = tracker.update(det_f2)
    assert len(tracks_f2) == 1
    assert tracks_f2[0].track_id == track_id
    assert len(events_f2) == 1  # Triggered!
    assert events_f2[0].track_id == track_id
    assert events_f2[0].material == MaterialCategory.ALUMINUM_CAN

    # Frame 3: Object continues past tripwire line (y: 250 to 330, cy = 290)
    det_f3 = [
        {
            "bbox": [53.0, 250.0, 93.0, 330.0],
            "material": MaterialCategory.ALUMINUM_CAN,
            "confidence": 0.94,
            "mass_grams": 14.2,
        }
    ]
    tracks_f3, events_f3 = tracker.update(det_f3)
    assert len(tracks_f3) == 1
    assert tracks_f3[0].track_id == track_id
    # Crucial guarantee: Zero double-counting!
    assert len(events_f3) == 0
    assert tracks_f3[0].counted is True


def test_synthetic_conveyor_generator():
    """Verify synthetic conveyor produces valid image and detections."""
    gen = SyntheticConveyorGenerator(width=640, height=480, speed=10.0)
    # Run multiple steps
    for _ in range(5):
        img, dets = gen.step()
    assert img.size == (640, 480)
    assert isinstance(dets, list)


def test_stream_endpoints():
    """Verify live snapshot, telemetry, and reset endpoints."""
    # Snapshot
    snap_resp = client.get("/api/stream/snapshot")
    assert snap_resp.status_code == 200
    assert snap_resp.headers["content-type"] == "image/jpeg"
    assert len(snap_resp.content) > 1000

    # Telemetry
    telem_resp = client.get("/api/stream/telemetry")
    assert telem_resp.status_code == 200
    telem_data = telem_resp.json()
    assert "items_total" in telem_data
    assert "total_avoided_co2e_kg" in telem_data

    # Reset
    reset_resp = client.post("/api/stream/reset")
    assert reset_resp.status_code == 200
    assert reset_resp.json()["status"] == "reset"
