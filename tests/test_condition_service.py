
import pytest

from src.services.condition_service import evaluate_temperature


@pytest.mark.parametrize(
    ("temperature_c", "expected_status"),
    [
        (1.9, "WARNING"),
        (2.0, "NORMAL"),
        (5.0, "NORMAL"),
        (8.0, "NORMAL"),
        (8.1, "WARNING"),
    ],
)
def test_temperature_rules(temperature_c, expected_status):
    assessment = evaluate_temperature(temperature_c)

    assert assessment.status == expected_status
    assert len(assessment.reasons) > 0
