
from fastapi import APIRouter, Query

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
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[TelemetryRecord]:
    return telemetry_service.list_journey_telemetry(
        journey_id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/boxes/{device_id}/telemetry",
    response_model=list[TelemetryRecord],
)
def get_device_telemetry(
    device_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[TelemetryRecord]:
    return telemetry_service.list_device_telemetry(
        device_id,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/boxes/{device_id}/journeys/{journey_id}/telemetry",
    response_model=list[TelemetryRecord],
)
def get_device_journey_telemetry(
    device_id: str,
    journey_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[TelemetryRecord]:
    return telemetry_service.list_device_journey_telemetry(
        device_id,
        journey_id,
        limit=limit,
        offset=offset,
    )
