
from fastapi import APIRouter

from src.schemas.telemetry import (
    TelemetryRecord,
    TelemetryRequest,
    TelemetryResponse,
)
from src.services import telemetry_service

router = APIRouter(prefix="/api/v1", tags=["Telemetry"])


@router.post("/telemetry", response_model=TelemetryResponse)
def receive_telemetry(
    telemetry: TelemetryRequest,
) -> TelemetryResponse:
    return telemetry_service.store_telemetry(telemetry)


@router.get(
    "/journeys/{journey_id}/telemetry",
    response_model=list[TelemetryRecord],
)
def get_journey_telemetry(
    journey_id: str,
) -> list[TelemetryRecord]:
    return telemetry_service.list_journey_telemetry(journey_id)
