"""
Predictive maintenance: estimate a machine's Remaining Useful Life (RUL) by fitting a
simple linear trend to its recent vibration readings and projecting forward to the point
it would cross the machine's configured safe limit.

Intentionally simple (no deep learning) — a transparent, explainable model, which matters
more than raw accuracy for a maintenance team that needs to trust and act on the number.
"""
import numpy as np
from datetime import timedelta
from django.utils import timezone


def predict_remaining_life(machine, lookback=60):
    readings = list(machine.readings.order_by("-recorded_at")[:lookback])
    if len(readings) < 10:
        return None

    readings = list(reversed(readings))
    t0 = readings[0].recorded_at
    xs = np.array([(r.recorded_at - t0).total_seconds() / 3600 for r in readings])
    ys = np.array([float(r.vibration_mm_s) for r in readings])

    slope, intercept = np.polyfit(xs, ys, 1)
    limit = float(machine.normal_vibration_max)

    # Treat a negligible slope the same as "stable" — avoids absurd (and overflow-prone)
    # multi-million-hour projections from essentially flat data with floating-point noise.
    if slope <= 1e-6:
        return {"trend": "stable_or_improving", "remaining_hours": None, "confidence": "low",
                "message": "Vibration is stable or decreasing — no imminent failure trend detected."}

    current_x = xs[-1]
    current_y = slope * current_x + intercept
    if current_y >= limit:
        return {"trend": "already_over_limit", "remaining_hours": 0, "confidence": "high",
                "message": "Vibration is already at or above the safe limit."}

    hours_to_limit = float((limit - current_y) / slope)
    if hours_to_limit > 100_000:  # >11 years out — not a meaningful near-term prediction
        return {"trend": "stable_or_improving", "remaining_hours": None, "confidence": "low",
                "message": "Degradation trend is too slow to project a meaningful failure date."}

    confidence = "high" if len(readings) >= 40 else "medium"
    return {
        "trend": "degrading",
        "remaining_hours": round(hours_to_limit, 1),
        "remaining_days": round(hours_to_limit / 24, 1),
        "predicted_failure_date": (timezone.now() + timedelta(hours=hours_to_limit)).date().isoformat(),
        "confidence": confidence,
        "message": f"At the current degradation rate, vibration will cross the safe limit in about {round(hours_to_limit / 24, 1)} days.",
    }
