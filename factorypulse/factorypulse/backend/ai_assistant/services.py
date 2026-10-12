"""
AI Maintenance Assistant.

Builds a context summary for a machine (recent sensor stats, anomaly history, open
work orders, predictive-maintenance trend) and asks an LLM to explain it in plain
language for a maintenance engineer.

Works with ANTHROPIC_API_KEY or OPENAI_API_KEY set in the environment. If neither is
configured, falls back to a rule-based explanation built from the same context data —
so the feature is fully demoable without any API key, and upgrades automatically to a
real LLM once a key is added.
"""
import os
import requests
from maintenance.predict import predict_remaining_life


def _build_context(machine):
    recent = list(machine.readings.order_by("-recorded_at")[:20])
    anomalies = [r for r in recent if r.is_anomaly]
    open_orders = machine.work_orders.exclude(status="completed").exclude(status="cancelled")
    prediction = predict_remaining_life(machine)

    return {
        "machine": f"{machine.name} ({machine.machine_code}, {machine.get_machine_type_display()})",
        "status": machine.status,
        "criticality": machine.criticality,
        "recent_readings_count": len(recent),
        "recent_anomalies_count": len(anomalies),
        "latest_vibration": float(recent[0].vibration_mm_s) if recent else None,
        "latest_temperature": float(recent[0].temperature_c) if recent else None,
        "normal_vibration_max": float(machine.normal_vibration_max),
        "open_work_orders": [{"title": o.title, "priority": o.priority} for o in open_orders],
        "prediction": prediction,
    }


def _fallback_explanation(ctx):
    lines = [f"Status for {ctx['machine']}:"]
    if ctx["recent_anomalies_count"] > 0:
        lines.append(
            f"{ctx['recent_anomalies_count']} of the last {ctx['recent_readings_count']} readings were flagged "
            f"as anomalies by the detection model. Latest vibration is {ctx['latest_vibration']} mm/s "
            f"(normal limit: {ctx['normal_vibration_max']} mm/s)."
        )
    else:
        lines.append(f"No anomalies in the last {ctx['recent_readings_count']} readings — operating within normal parameters.")

    pred = ctx.get("prediction")
    if pred and pred.get("trend") == "degrading":
        lines.append(pred["message"])
    elif pred and pred.get("trend") == "already_over_limit":
        lines.append("Vibration is already above the safe limit — this machine needs attention soon.")

    if ctx["open_work_orders"]:
        titles = ", ".join(o["title"] for o in ctx["open_work_orders"])
        lines.append(f"Open work orders: {titles}.")
    else:
        lines.append("No open work orders for this machine.")

    lines.append(
        "(This is a rule-based summary. Set ANTHROPIC_API_KEY or OPENAI_API_KEY in the "
        "environment for a full natural-language explanation from an LLM.)"
    )
    return " ".join(lines)


def _call_anthropic(prompt, api_key):
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        json={"model": "claude-sonnet-4-5", "max_tokens": 400, "messages": [{"role": "user", "content": prompt}]},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    return "".join(block.get("text", "") for block in data.get("content", []))


def _call_openai(prompt, api_key):
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "content-type": "application/json"},
        json={"model": "gpt-4o-mini", "max_tokens": 400, "messages": [{"role": "user", "content": prompt}]},
        timeout=20,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def explain_machine(machine, question=None):
    ctx = _build_context(machine)
    prompt = (
        "You are a plant maintenance assistant. Given this machine telemetry summary, "
        "explain what's happening in plain, practical language for a maintenance engineer, "
        "and recommend a clear next action. Keep it under 150 words.\n\n"
        f"Context: {ctx}\n\n"
    )
    if question:
        prompt += f'The engineer specifically asked: "{question}"\n'

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    try:
        if anthropic_key:
            return {"source": "anthropic", "answer": _call_anthropic(prompt, anthropic_key), "context": ctx}
        if openai_key:
            return {"source": "openai", "answer": _call_openai(prompt, openai_key), "context": ctx}
    except Exception as exc:
        return {"source": "fallback", "answer": _fallback_explanation(ctx), "context": ctx, "llm_error": str(exc)}

    return {"source": "fallback", "answer": _fallback_explanation(ctx), "context": ctx}
