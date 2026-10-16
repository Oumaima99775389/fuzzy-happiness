
from src.schemas.telemetry import TelemetryRequest, TelemetryResponse


def validate_telemetry(
    telemetry: TelemetryRequest,
) -> TelemetryResponse:
    return TelemetryResponse(
        status="validated",
        device_id=telemetry.device_id,
        journey_id=telemetry.journey_id,
        timestamp=telemetry.timestamp,
    )
