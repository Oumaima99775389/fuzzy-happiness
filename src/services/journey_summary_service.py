
from src.repositories import (
    condition_event_repository,
    telemetry_repository,
)
from src.schemas.journey_summary import (
    EventSummary,
    JourneySummary,
    TemperatureSummary,
    VibrationSummary,
)


def get_journey_summary(journey_id: str) -> JourneySummary:
    telemetry = telemetry_repository.get_journey_summary(journey_id)

    events = condition_event_repository.get_journey_event_summary(
        journey_id
    )

    return JourneySummary(
        journey_id=journey_id,
        total_readings=telemetry["total_readings"],
        temperature=TemperatureSummary(
            min=telemetry["min_temperature"],
            max=telemetry["max_temperature"],
            average=telemetry["average_temperature"],
        ),
        vibration=VibrationSummary(
            min=telemetry["min_vibration"],
            max=telemetry["max_vibration"],
            average=telemetry["average_vibration"],
        ),
        events=EventSummary(
            high_temperature=events["high_temperature"],
            low_temperature=events["low_temperature"],
            active=events["active"],
        ),
    )
