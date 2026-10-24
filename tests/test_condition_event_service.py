
from datetime import datetime, timezone

import pytest

from src.repositories import condition_event_repository as repository
from src.services import condition_event_service as service


@pytest.fixture
def event_database(tmp_path, monkeypatch):
    """Give each test its own temporary SQLite database."""
    monkeypatch.setattr(
        repository,
        "DB_PATH",
        tmp_path / "telemetry.db",
    )
    repository.initialize_condition_event_table()


@pytest.fixture
def observed_at():
    return datetime(2026, 10, 24, 10, 0, tzinfo=timezone.utc)


def test_high_temperature_creates_event(event_database, observed_at):
    events = service.process_temperature_reading(
        "box-001", "journey-001", 9.0, observed_at
    )

    assert len(events) == 1
    assert events[0].event_type == "TEMPERATURE_HIGH"
    assert events[0].status == "ACTIVE"
    assert events[0].started_at == observed_at


def test_repeated_high_reading_does_not_create_duplicate(
    event_database, observed_at
):
    service.process_temperature_reading(
        "box-001", "journey-001", 9.0, observed_at
    )

    later = datetime(2026, 10, 24, 10, 1, tzinfo=timezone.utc)
    events = service.process_temperature_reading(
        "box-001", "journey-001", 10.0, later
    )

    assert len(events) == 1
    assert events[0].event_type == "TEMPERATURE_HIGH"
    assert events[0].status == "ACTIVE"

    stored_events = repository.list_events("box-001", "journey-001")
    assert len(stored_events) == 1


def test_normal_reading_closes_active_event(event_database, observed_at):
    service.process_temperature_reading(
        "box-001", "journey-001", 9.0, observed_at
    )

    recovery_time = datetime(2026, 10, 24, 10, 5, tzinfo=timezone.utc)
    events = service.process_temperature_reading(
        "box-001", "journey-001", 7.0, recovery_time
    )

    assert len(events) == 1
    assert events[0].status == "CLOSED"
    assert events[0].ended_at == recovery_time


def test_low_temperature_creates_low_event(event_database, observed_at):
    events = service.process_temperature_reading(
        "box-001", "journey-001", 1.0, observed_at
    )

    assert len(events) == 1
    assert events[0].event_type == "TEMPERATURE_LOW"
    assert events[0].status == "ACTIVE"


def test_high_to_low_transition_closes_high_event(
    event_database, observed_at
):
    service.process_temperature_reading(
        "box-001", "journey-001", 9.0, observed_at
    )

    later = datetime(2026, 10, 24, 10, 1, tzinfo=timezone.utc)
    events = service.process_temperature_reading(
        "box-001", "journey-001", 1.0, later
    )

    assert len(events) == 2

    stored_events = repository.list_events("box-001", "journey-001")
    assert len(stored_events) == 2

    high_event = next(
        event for event in stored_events
        if event.event_type == "TEMPERATURE_HIGH"
    )
    low_event = next(
        event for event in stored_events
        if event.event_type == "TEMPERATURE_LOW"
    )

    assert high_event.status == "CLOSED"
    assert high_event.ended_at == later
    assert low_event.status == "ACTIVE"
