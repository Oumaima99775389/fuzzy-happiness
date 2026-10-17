import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from src.schemas.telemetry import TelemetryRequest


from src.app import app


client = TestClient(app)

VALID_PAYLOAD = {
    "device_id": "esp32-box-001",
    "journey_id": "journey-001",
    "timestamp": "2026-10-17T08:30:00Z",
    "temperature_c": 5.4,
    "vibration_g": 0.12,
}


def test_health_endpoint():
    response = client.get("/healthCheck")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_valid_telemetry_is_acknowledged():
    response = client.post(
        "/api/v1/telemetry",
        json=VALID_PAYLOAD,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "stored"
    assert data["device_id"] == VALID_PAYLOAD["device_id"]
    assert data["journey_id"] == VALID_PAYLOAD["journey_id"]


def test_missing_required_field_is_rejected():
    payload = VALID_PAYLOAD.copy()
    payload.pop("temperature_c")

    response = client.post("/api/v1/telemetry", json=payload)

    assert response.status_code == 422


def test_empty_device_id_is_rejected():
    payload = {**VALID_PAYLOAD, "device_id": ""}

    response = client.post("/api/v1/telemetry", json=payload)

    assert response.status_code == 422


def test_timestamp_without_timezone_is_rejected():
    payload = {
        **VALID_PAYLOAD,
        "timestamp": "2026-10-17T08:30:00",
    }

    response = client.post("/api/v1/telemetry", json=payload)

    assert response.status_code == 422



def test_out_of_range_temperature_is_rejected():
    payload = {
        **VALID_PAYLOAD,
        "temperature_c": 120,
    }

    response = client.post(
        "/api/v1/telemetry",
        json=payload,
    )

    assert response.status_code == 422



def test_nan_temperature_is_rejected_by_schema():
    with pytest.raises(ValidationError):
        TelemetryRequest(
            device_id="esp32-box-001",
            journey_id="journey-001",
            timestamp="2026-10-17T08:30:00Z",
            temperature_c=float("nan"),
            vibration_g=0.12,
        )

def test_telemetry_is_saved_and_retrieved(monkeypatch, tmp_path):
    from src.repositories import telemetry_repository

    monkeypatch.setattr(
        telemetry_repository,
        "DB_PATH",
        tmp_path / "test_telemetry.db",
    )

    post_response = client.post(
        "/api/v1/telemetry",
        json=VALID_PAYLOAD,
    )

    assert post_response.status_code == 200
    assert post_response.json()["status"] == "stored"

    get_response = client.get(
        "/api/v1/journeys/journey-001/telemetry"
    )

    assert get_response.status_code == 200

    readings = get_response.json()
    assert len(readings) == 1
    assert readings[0]["device_id"] == "esp32-box-001"
    assert readings[0]["temperature_c"] == 5.4
    assert readings[0]["vibration_g"] == 0.12

