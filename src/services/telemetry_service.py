from src.repositories import telemetry_repository
from src.schemas.telemetry import (
    ConditionAssessmentResponse,
    TelemetryRecord,
    TelemetryRequest,
    TelemetryResponse,
)
from src.services import condition_service


def store_telemetry(
    telemetry: TelemetryRequest,
) -> TelemetryResponse:
    telemetry_repository.save_telemetry(telemetry)

    assessment = condition_service.evaluate_temperature(
        telemetry.temperature_c
    )

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
    return [TelemetryRecord(**row) for row in rows]


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
    return [TelemetryRecord(**row) for row in rows]


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
    return [TelemetryRecord(**row) for row in rows]

def store_telemetry(
    telemetry: TelemetryRequest,
) -> TelemetryResponse:
    telemetry_repository.save_telemetry(telemetry)

    assessment = condition_service.evaluate_temperature(
        telemetry.temperature_c
    )

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