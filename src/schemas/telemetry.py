from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TelemetryBase(BaseModel):
    """Shared configuration for telemetry models."""

    model_config = ConfigDict(extra="forbid")


class TelemetryRequest(TelemetryBase):
    """Validate incoming telemetry data."""

    device_id: str = Field(min_length=1, max_length=64)
    journey_id: str = Field(min_length=1, max_length=64)
    timestamp: datetime
    temperature_c: float = Field(ge=-40, le=85)
    vibration_g: float = Field(ge=0, le=16)


class TelemetryResponse(TelemetryBase):
    """Define the telemetry API response."""

    status: str
    device_id: str
    journey_id: str
    timestamp: datetime

class TelemetryResponse2(TelemetryBase):
    """Define the telemetry API response."""

    status: str
    device_id: str
    journey_id: str
    timestamp: datetime
    temperature_c: float
    vibration_g: float