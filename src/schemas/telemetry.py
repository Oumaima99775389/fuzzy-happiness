
from datetime import datetime
import math

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


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

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_have_timezone(
        cls, value: datetime
    ) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Timestamp must include timezone information")
        return value

    @field_validator("temperature_c", "vibration_g")
    @classmethod
    def values_must_be_finite(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("Value must be finite")
        return value


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

class TelemetryRecord(BaseModel):
    """A telemetry reading retrieved from local storage."""

    id: int
    device_id: str
    journey_id: str
    timestamp: datetime
    temperature_c: float
    vibration_g: float
