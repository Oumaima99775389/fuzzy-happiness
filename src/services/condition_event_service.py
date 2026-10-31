
import sqlite3
from datetime import datetime

from src.repositories import condition_event_repository as repository
from src.schemas.condition_event import ConditionEvent
from src.services.condition_service import (
    MIN_TEMPERATURE_C,
    MAX_TEMPERATURE_C,
)


def process_temperature_reading(
    device_id: str,
    journey_id: str,
    temperature_c: float,
    observed_at: datetime,
    connection: sqlite3.Connection | None = None,
) -> list[ConditionEvent]:
    """Update temperature events based on a new reading."""

    if observed_at.tzinfo is None or observed_at.utcoffset() is None:
        raise ValueError("observed_at must be timezone-aware.")

    if temperature_c > MAX_TEMPERATURE_C:
        current_type = "TEMPERATURE_HIGH"
        opposite_type = "TEMPERATURE_LOW"
    elif temperature_c < MIN_TEMPERATURE_C:
        current_type = "TEMPERATURE_LOW"
        opposite_type = "TEMPERATURE_HIGH"
    else:
        current_type = None
        opposite_type = None

    updated_events: list[ConditionEvent] = []

    # Close an event of the opposite type if the condition changes.
    if opposite_type is not None:
        opposite_event = repository.find_active_event(
            device_id,
            journey_id,
            opposite_type,
            connection=connection,
        )
        if opposite_event is not None:
            closed_event = repository.close_event(
                opposite_event["id"],
                observed_at,
                connection=connection,
            )
            if closed_event is not None:
                updated_events.append(closed_event)

    # A normal reading closes any active temperature events.
    if current_type is None:
        for event_type in ("TEMPERATURE_HIGH", "TEMPERATURE_LOW"):
            active_event = repository.find_active_event(
                device_id,
                journey_id,
                event_type,
                connection=connection,
            )
            if active_event is not None:
                closed_event = repository.close_event(
                    active_event["id"],
                    observed_at,
                    connection=connection,
                )
                if closed_event is not None:
                    updated_events.append(closed_event)

        return updated_events

    # Reuse the active event instead of creating duplicates.
    active_event = repository.find_active_event(
        device_id,
        journey_id,
        current_type,
        connection=connection,
    )

    if active_event is not None:
        existing_event = repository.get_event_by_id(
            active_event["id"],
            connection=connection,
        )
        return updated_events + (
            [existing_event] if existing_event is not None else []
        )

    # No active event exists, so start a new incident.
    new_event = repository.create_event(
        device_id=device_id,
        journey_id=journey_id,
        event_type=current_type,
        started_at=observed_at,
        connection=connection,
    )
    updated_events.append(new_event)

    return updated_events
