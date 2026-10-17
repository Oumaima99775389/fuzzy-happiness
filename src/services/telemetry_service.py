
from src.repositories import telemetry_repository
from src.schemas.telemetry import (
    TelemetryRecord,
    TelemetryRequest,
    TelemetryResponse,
)


def store_telemetry(
    telemetry: TelemetryRequest,
) -> TelemetryResponse:
    telemetry_repository.save_telemetry(telemetry)

    return TelemetryResponse(
        status="stored",
        device_id=telemetry.device_id,
        journey_id=telemetry.journey_id,
        timestamp=telemetry.timestamp,
    )


def list_journey_telemetry(
    journey_id: str,
) -> list[TelemetryRecord]:
    rows = telemetry_repository.get_telemetry_for_journey(journey_id)
    return [TelemetryRecord(**row) for row in rows]
