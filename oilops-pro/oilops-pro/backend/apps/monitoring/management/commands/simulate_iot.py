import random
import time

from django.core.management.base import BaseCommand

from apps.equipment.models import Equipment
from apps.monitoring.services import ingest_reading

# metric -> (normal mean, noise, spike size)
PROFILES = {
    "TEMPERATURE": (78, 4, 45), "PRESSURE": (42, 3, 28), "VOLTAGE": (400, 8, 70),
    "VIBRATION": (2.5, 0.5, 6), "OIL_LEVEL": (72, 4, -45),
}
APPLIES = {
    "PUMP": ["TEMPERATURE", "PRESSURE", "VIBRATION", "OIL_LEVEL"],
    "COMPRESSOR": ["TEMPERATURE", "PRESSURE", "VIBRATION", "OIL_LEVEL"],
    "VALVE": ["PRESSURE", "TEMPERATURE"],
    "GENERATOR": ["TEMPERATURE", "VOLTAGE", "VIBRATION", "OIL_LEVEL"],
    "TURBINE": ["TEMPERATURE", "PRESSURE", "VIBRATION", "VOLTAGE", "OIL_LEVEL"],
    "SENSOR": ["TEMPERATURE", "VOLTAGE"],
}


class Command(BaseCommand):
    help = "Generate simulated IoT telemetry (with occasional spikes) to exercise alerts."

    def add_arguments(self, p):
        p.add_argument("--rounds", type=int, default=5)
        p.add_argument("--interval", type=float, default=0.0, help="seconds between rounds")
        p.add_argument("--spike-chance", type=float, default=0.03)

    def handle(self, *a, **o):
        eqs = list(Equipment.objects.exclude(status__in=["DECOMMISSIONED", "OFFLINE"]))
        total = alerts = 0
        for r in range(o["rounds"]):
            for eq in eqs:
                for metric in APPLIES.get(eq.category, []):
                    mean, noise, spike = PROFILES[metric]
                    val = random.gauss(mean, noise)
                    if random.random() < o["spike_chance"]:
                        val += spike
                    _, alert = ingest_reading(eq, metric, round(val, 2))
                    total += 1
                    alerts += 1 if alert else 0
            self.stdout.write(f"round {r + 1}/{o['rounds']}: {total} readings, {alerts} alert events")
            if o["interval"] and r < o["rounds"] - 1:
                time.sleep(o["interval"])
