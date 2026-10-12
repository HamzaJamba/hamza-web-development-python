"""
Lightweight, in-process anomaly detection for sensor readings.

For each machine, train a scikit-learn IsolationForest on that machine's recent reading
history (vibration, temperature, pressure, rpm). The model is cached in memory per
machine and retrained periodically as new data comes in — genuine, trained-on-the-data
ML rather than hardcoded thresholds.

If a machine doesn't have enough history yet, fall back to the machine's configured
"normal_*" operating limits so the system still flags obviously bad readings from day one.
"""
import numpy as np
from sklearn.ensemble import IsolationForest

MIN_SAMPLES_FOR_ML = 25
RETRAIN_EVERY = 20

_model_cache = {}


def _features(readings):
    return np.array([[float(r.vibration_mm_s), float(r.temperature_c), float(r.pressure_bar), float(r.rpm)] for r in readings])


def _train(machine):
    history = list(machine.readings.order_by("-recorded_at")[:300])
    if len(history) < MIN_SAMPLES_FOR_ML:
        return None
    X = _features(history)
    model = IsolationForest(n_estimators=100, contamination=0.08, random_state=42)
    model.fit(X)
    _model_cache[machine.id] = {"model": model, "trained_count": len(history)}
    return model


def _get_model(machine):
    cached = _model_cache.get(machine.id)
    count = machine.readings.count()
    if cached is None or count - cached["trained_count"] >= RETRAIN_EVERY:
        return _train(machine)
    return cached["model"]


def score_reading(machine, vibration, temperature, pressure, rpm):
    """Returns (is_anomaly: bool, anomaly_score: float|None)."""
    model = _get_model(machine)
    if model is None:
        is_anomaly = (
            vibration > float(machine.normal_vibration_max)
            or temperature > float(machine.normal_temperature_max)
            or pressure > float(machine.normal_pressure_max)
        )
        return is_anomaly, None

    X = np.array([[vibration, temperature, pressure, rpm]])
    pred = model.predict(X)[0]
    score = float(model.decision_function(X)[0])
    return pred == -1, score
