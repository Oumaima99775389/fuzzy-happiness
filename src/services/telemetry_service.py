from src.repositories import telemetry_repository
from src.schemas.telemetry import (
    ConditionAssessmentResponse,
    TelemetryRecord,
    TelemetryRequest,
    TelemetryResponse,
)
from src.services import condition_service
from src.services import condition_event_service



def store_telemetry(
    telemetry: TelemetryRequest,
) -> TelemetryResponse:
    # 1. Persist the raw reading first.
    telemetry_repository.save_telemetry(telemetry)

    # 2. Evaluate the temperature for the API response.
    assessment = condition_service.evaluate_temperature(
        telemetry.temperature_c
    )

    # 3. Create, maintain, or close temperature events.
    condition_event_service.process_temperature_reading(
        device_id=telemetry.device_id,
        journey_id=telemetry.journey_id,
        temperature_c=telemetry.temperature_c,
        observed_at=telemetry.timestamp,
    )

    # 4. Return the existing API response structure.
    return TelemetryResponse(
        status="stored",
        device_id=telemetry.device_id,
        journey_id=telemetry.journey_id,
        timestamp=telemetry.timestamp,
        condition=ConditionAssessmentResponse(
            status=assessment.status,
            reasons=assessment.reasons,
        ),
    )

def _build_telemetry_record(row: dict) -> TelemetryRecord:
    """Convert a database row into a complete telemetry record."""

    assessment = condition_service.evaluate_temperature(
        row["temperature_c"]
    )

    return TelemetryRecord(
        **row,
        condition=ConditionAssessmentResponse(
            status=assessment.status,
            reasons=assessment.reasons,
        ),
    )


def list_journey_telemetry(
    journey_id: str,
    limit: int = 100,
    offset: int = 0,
) -> list[TelemetryRecord]:
    rows = telemetry_repository.get_telemetry_for_journey(
        journey_id,
        limit=limit,
        offset=offset,
    )
    return [_build_telemetry_record(row) for row in rows]


def list_device_telemetry(
    device_id: str,
    limit: int = 100,
    offset: int = 0,
) -> list[TelemetryRecord]:
    rows = telemetry_repository.get_telemetry_for_device(
        device_id,
        limit=limit,
        offset=offset,
    )
    return [_build_telemetry_record(row) for row in rows]


def list_device_journey_telemetry(
    device_id: str,
    journey_id: str,
    limit: int = 100,
    offset: int = 0,
) -> list[TelemetryRecord]:
    rows = telemetry_repository.get_telemetry_for_device_journey(
        device_id,
        journey_id,
        limit=limit,
        offset=offset,
    )
    return [_build_telemetry_record(row) for row in rows]
