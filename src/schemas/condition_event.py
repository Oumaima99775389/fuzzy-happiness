
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ConditionEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int
    device_id: str
    journey_id: str
    event_type: Literal["TEMPERATURE_HIGH", "TEMPERATURE_LOW"]
    started_at: datetime
    ended_at: datetime | None = None
    status: Literal["ACTIVE", "CLOSED"]
