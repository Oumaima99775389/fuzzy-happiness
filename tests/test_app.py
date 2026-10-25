import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from src.schemas.telemetry import TelemetryRequest
from src.repositories import telemetry_repository
from src.repositories import condition_event_repository


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


def test_telemetry_can_be_filtered_by_device_and_journey(
    monkeypatch,
    tmp_path,
):
    from fastapi.testclient import TestClient
    from src.app import app

    monkeypatch.setattr(
        telemetry_repository,
        "DB_PATH",
        tmp_path / "test_telemetry.db",
    )

    client = TestClient(app)

    readings = [
        {
            "device_id": "box-001",
            "journey_id": "journey-A",
            "timestamp": "2026-10-19T09:00:00Z",
            "temperature_c": 4.0,
            "vibration_g": 0.2,
        },
        {
            "device_id": "box-001",
            "journey_id": "journey-B",
            "timestamp": "2026-10-19T10:00:00Z",
            "temperature_c": 5.0,
            "vibration_g": 0.3,
        },
        {
            "device_id": "box-002",
            "journey_id": "journey-A",
            "timestamp": "2026-10-19T11:00:00Z",
            "temperature_c": 3.5,
            "vibration_g": 0.1,
        },
    ]

    for reading in readings:
        response = client.post("/api/v1/telemetry", json=reading)
        assert response.status_code == 200

    # All readings for box-001
    response = client.get("/api/v1/boxes/box-001/telemetry")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(
        item["device_id"] == "box-001"
        for item in response.json()
    )

    # Readings for one box during one journey
    response = client.get(
        "/api/v1/boxes/box-001/journeys/journey-A/telemetry"
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["journey_id"] == "journey-A"

    # Existing journey endpoint still works
    response = client.get(
        "/api/v1/journeys/journey-A/telemetry"
    )
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Pagination returns only the requested number of rows
    response = client.get(
        "/api/v1/boxes/box-001/telemetry?limit=1&offset=0"
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Invalid limits are rejected by FastAPI
    response = client.get(
        "/api/v1/boxes/box-001/telemetry?limit=0"
    )
    assert response.status_code == 422


def test_telemetry_response_includes_normal_condition():
    payload = {
        "device_id": "box-001",
        "journey_id": "journey-001",
        "timestamp": "2026-10-21T08:30:00Z",
        "temperature_c": 5.0,
        "vibration_g": 0.12,
    }

    response = client.post("/api/v1/telemetry", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "stored"
    assert data["condition"]["status"] == "NORMAL"
    assert data["condition"]["reasons"]


def test_telemetry_response_includes_temperature_warning():
    payload = {
        "device_id": "box-001",
        "journey_id": "journey-001",
        "timestamp": "2026-10-21T08:31:00Z",
        "temperature_c": 9.0,
        "vibration_g": 0.12,
    }

    response = client.post("/api/v1/telemetry", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["condition"]["status"] == "WARNING"
    assert data["condition"]["reasons"]

@pytest.fixture(autouse=True)
def use_test_database(monkeypatch, tmp_path):
    """Give each test its own isolated SQLite database."""
    db_path = tmp_path / "test_telemetry.db"

    monkeypatch.setattr(
        telemetry_repository,
        "DB_PATH",
        db_path,
    )
    monkeypatch.setattr(
        condition_event_repository,
        "DB_PATH",
        db_path,
    )

    # Create both tables in the temporary database.
    telemetry_repository.initialize_database()
    condition_event_repository.initialize_condition_event_table()

def test_pagination_offset_skips_existing_readings():
    payloads = [
        {
            **VALID_PAYLOAD,
            "timestamp": "2026-10-17T08:30:00Z",
            "temperature_c": 4.0,
        },
        {
            **VALID_PAYLOAD,
            "timestamp": "2026-10-17T08:31:00Z",
            "temperature_c": 5.0,
        },
        {
            **VALID_PAYLOAD,
            "timestamp": "2026-10-17T08:32:00Z",
            "temperature_c": 6.0,
        },
    ]

    for payload in payloads:
        response = client.post("/api/v1/telemetry", json=payload)
        assert response.status_code == 200

    response = client.get(
        "/api/v1/journeys/journey-001/telemetry?limit=1&offset=1"
    )

    assert response.status_code == 200
    readings = response.json()
    assert len(readings) == 1
    assert readings[0]["temperature_c"] == 5.0


def test_empty_journey_returns_empty_list():
    response = client.get(
        "/api/v1/journeys/nonexistent-journey/telemetry"
    )

    assert response.status_code == 200
    assert response.json() == []


def test_high_temperature_creates_condition_event():
    payload = {
        **VALID_PAYLOAD,
        "device_id": "esp32-box-high",
        "journey_id": "journey-high",
        "temperature_c": 10.0,
    }

    response = client.post("/api/v1/telemetry", json=payload)

    assert response.status_code == 200

    events = condition_event_repository.list_events(
        device_id="esp32-box-high",
        journey_id="journey-high",
    )

    assert len(events) == 1
    assert events[0].event_type == "TEMPERATURE_HIGH"
    assert events[0].status == "ACTIVE"


def test_normal_temperature_closes_active_condition_event():
    high_payload = {
        **VALID_PAYLOAD,
        "device_id": "esp32-box-close",
        "journey_id": "journey-close",
        "temperature_c": 10.0,
    }

    normal_payload = {
        **high_payload,
        "temperature_c": 5.0,
        "timestamp": "2026-10-17T09:30:00Z",
    }

    client.post("/api/v1/telemetry", json=high_payload)
    response = client.post("/api/v1/telemetry", json=normal_payload)

    assert response.status_code == 200

    events = condition_event_repository.list_events(
        device_id="esp32-box-close",
        journey_id="journey-close",
    )

    assert len(events) == 1
    assert events[0].event_type == "TEMPERATURE_HIGH"
    assert events[0].status == "CLOSED"
    assert events[0].ended_at is not None
