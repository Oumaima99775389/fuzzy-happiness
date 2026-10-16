from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/healthCheck")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_valid_telemetry_is_acknowledged():
    payload = {
        "device_id": "esp32-box-001",
        "journey_id": "journey-001",
        "timestamp": "2026-10-16T08:30:00Z",
        "temperature_c": 5.4,
        "vibration_g": 0.12,
    }

    response = client.post("/api/v1/telemetry", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "validated"
    assert response.json()["device_id"] == "esp32-box-001"
    assert response.json()["journey_id"] == "journey-001"


def test_out_of_range_temperature_is_rejected():
    payload = {
        "device_id": "esp32-box-001",
        "journey_id": "journey-001",
        "timestamp": "2026-10-16T08:30:00Z",
        "temperature_c": 120,
        "vibration_g": 0.12,
    }

    response = client.post("/api/v1/telemetry", json=payload)

    assert response.status_code == 422


def test_unknown_fields_are_rejected():
    payload = {
        "device_id": "esp32-box-001",
        "journey_id": "journey-001",
        "timestamp": "2026-10-16T08:30:00Z",
        "temperature_c": 5.4,
        "vibration_g": 0.12,
        "temperatur_c": 5.4,
    }

    response = client.post("/api/v1/telemetry", json=payload)

    assert response.status_code == 422



