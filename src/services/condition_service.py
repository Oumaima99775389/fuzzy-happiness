
from dataclasses import dataclass


MIN_TEMPERATURE_C = 2.0
MAX_TEMPERATURE_C = 8.0


@dataclass(frozen=True)
class ConditionAssessment:
    status: str
    reasons: list[str]


def evaluate_temperature(
    temperature_c: float,
) -> ConditionAssessment:
    if temperature_c < MIN_TEMPERATURE_C:
        return ConditionAssessment(
            status="WARNING",
            reasons=[
                "Temperature is below the configured minimum."
            ],
        )

    if temperature_c > MAX_TEMPERATURE_C:
        return ConditionAssessment(
            status="WARNING",
            reasons=[
                "Temperature is above the configured maximum."
            ],
        )

    return ConditionAssessment(
        status="NORMAL",
        reasons=[
            "Temperature is within the configured range."
        ],
    )
