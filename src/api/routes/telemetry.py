
from fastapi import APIRouter

from src.schemas.telemetry import TelemetryRequest, TelemetryResponse
from src.services.telemetry_service import validate_telemetry

router = APIRouter(prefix="/api/v1", tags=["Telemetry"])


@router.post("/telemetry", response_model=TelemetryResponse)
def receive_telemetry(
    telemetry: TelemetryRequest,
) -> TelemetryResponse:
    return validate_telemetry(telemetry)
