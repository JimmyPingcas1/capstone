"""
DO threshold and recommendation helpers.

This module is used by ai_do_prediction_service.py to classify DO risk
and generate operator recommendations.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DOThreshold:
    """Configurable dissolved oxygen thresholds in mg/L."""

    critical_low: float = 3.0
    low: float = 5.0
    optimal_min: float = 5.0
    optimal_max: float = 9.0
    high: float = 12.0


def get_do_risk_level(do_value: float, thresholds: Optional[DOThreshold] = None) -> str:
    """Return DO risk label using the provided or default thresholds."""
    t = thresholds or DOThreshold()

    if do_value < t.critical_low:
        return "CRITICAL_LOW"
    if do_value < t.low:
        return "LOW"
    if do_value <= t.optimal_max and do_value >= t.optimal_min:
        return "OPTIMAL"
    if do_value <= t.high:
        return "HIGH"
    return "VERY_HIGH"


def get_do_recommendations(
    do_value: float,
    temperature: float,
    thresholds: Optional[DOThreshold] = None,
) -> List[str]:
    """Generate practical recommendations based on DO and temperature."""
    t = thresholds or DOThreshold()
    recs: List[str] = []

    if do_value < t.critical_low:
        recs.append("Turn on aeration immediately.")
        recs.append("Reduce feeding until oxygen stabilizes.")
        recs.append("Check fish behavior and remove organic waste.")
    elif do_value < t.low:
        recs.append("Increase aeration to improve oxygen levels.")
        recs.append("Monitor ammonia and turbidity closely.")
    elif do_value > t.high:
        recs.append("DO is high; verify sensor calibration.")
        recs.append("Reduce unnecessary aeration if fish are stable.")
    else:
        recs.append("DO is within acceptable range.")

    if temperature >= 30.0:
        recs.append("High water temperature can reduce oxygen availability.")

    return recs
