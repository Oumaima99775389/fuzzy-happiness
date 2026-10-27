
from pydantic import BaseModel


class TemperatureSummary(BaseModel):
    min: float | None
    max: float | None
    average: float | None


class VibrationSummary(BaseModel):
    min: float | None
    max: float | None
    average: float | None


class EventSummary(BaseModel):
    high_temperature: int
    low_temperature: int
    active: int


class JourneySummary(BaseModel):
    journey_id: str
    total_readings: int
    temperature: TemperatureSummary
    vibration: VibrationSummary
    events: EventSummary
