from src.repositories import (
    condition_event_repository,
    telemetry_repository,
)
from src.services import journey_summary_service


def test_get_journey_summary_combines_repository_results(monkeypatch):
    monkeypatch.setattr(
        telemetry_repository,
        "get_journey_summary",
        lambda journey_id: {
            "total_readings": 2,
            "min_temperature": 4.0,
            "max_temperature": 6.0,
            "average_temperature": 5.0,
            "min_vibration": 0.1,
            "max_vibration": 0.3,
            "average_vibration": 0.2,
        },
    )

    monkeypatch.setattr(
        condition_event_repository,
        "get_journey_event_summary",
        lambda journey_id: {
            "high_temperature": 1,
            "low_temperature": 0,
            "active": 1,
        },
    )

    summary = journey_summary_service.get_journey_summary(
        "journey-001"
    )

    assert summary.journey_id == "journey-001"
    assert summary.total_readings == 2
    assert summary.temperature.average == 5.0
    assert summary.vibration.max == 0.3
    assert summary.events.high_temperature == 1
    assert summary.events.active == 1