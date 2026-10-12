import random
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from equipment.models import Machine
from sensors.models import SensorReading
from sensors.ml import score_reading
from maintenance.models import WorkOrder
from roles.models import Role

User = get_user_model()
PASSWORD = "Demo@12345"

MACHINES = [
    ("Compressor Line A", "CMP-A01", Machine.COMPRESSOR, "Utility Block", "critical", 6.5, 85, 12),
    ("Compressor Line B", "CMP-B02", Machine.COMPRESSOR, "Utility Block", "high", 6.5, 85, 12),
    ("Conveyor Belt 1", "CNV-01", Machine.CONVEYOR, "Assembly Floor", "medium", 4.0, 60, 5),
    ("Conveyor Belt 2", "CNV-02", Machine.CONVEYOR, "Assembly Floor", "medium", 4.0, 60, 5),
    ("Main Drive Motor", "MOT-01", Machine.MOTOR, "Power House", "critical", 5.0, 90, 8),
    ("Cooling Water Pump", "PMP-01", Machine.PUMP, "Utility Block", "high", 4.5, 70, 10),
    ("CNC Mill #3", "CNC-03", Machine.CNC, "Machining Shop", "medium", 3.5, 55, 6),
    ("Steam Turbine", "TRB-01", Machine.TURBINE, "Power House", "critical", 7.0, 110, 15),
]


class Command(BaseCommand):
    help = "Seed demo machines, historical sensor readings (with realistic degradation + anomalies), and work orders."

    def handle(self, *args, **opts):
        random.seed(11)
        roles = {n: Role.get(n) for n, _ in Role.ROLE_CHOICES}

        admin, c = User.objects.get_or_create(email="admin@factorypulse.io", defaults=dict(
            first_name="Plant", last_name="Admin", is_staff=True, is_superuser=True, role=roles["admin"]))
        if c: admin.set_password(PASSWORD); admin.save()

        manager, c = User.objects.get_or_create(email="manager@factorypulse.io", defaults=dict(
            first_name="Plant", last_name="Manager", role=roles["plant_manager"]))
        if c: manager.set_password(PASSWORD); manager.save()

        engineer, c = User.objects.get_or_create(email="engineer@factorypulse.io", defaults=dict(
            first_name="Maintenance", last_name="Engineer", role=roles["maintenance_engineer"]))
        if c: engineer.set_password(PASSWORD); engineer.save()

        operator, c = User.objects.get_or_create(email="operator@factorypulse.io", defaults=dict(
            first_name="Floor", last_name="Operator", role=roles["operator"]))
        if c: operator.set_password(PASSWORD); operator.save()

        machines = []
        for name, code, mtype, section, crit, vib_max, temp_max, press_max in MACHINES:
            m, _ = Machine.objects.update_or_create(
                machine_code=code,
                defaults=dict(name=name, machine_type=mtype, plant_section=section, criticality=crit,
                              location=section, manufacturer="Siemens", status=Machine.RUNNING,
                              normal_vibration_max=Decimal(str(vib_max)), normal_temperature_max=Decimal(str(temp_max)),
                              normal_pressure_max=Decimal(str(press_max))))
            machines.append(m)

        now = timezone.now()
        n_readings = 0
        for m in machines:
            if m.readings.exists():
                continue
            # one machine (Steam Turbine) gets an obvious degradation trend + anomalies for a good demo
            degrading = m.machine_code == "TRB-01"
            base_vib = float(m.normal_vibration_max) * 0.4
            for i in range(200):
                t = now - timedelta(minutes=(200 - i) * 12)
                drift = (i / 200) * float(m.normal_vibration_max) * 0.9 if degrading else 0
                noise = random.uniform(-0.15, 0.15) * float(m.normal_vibration_max)
                vib = max(0.1, base_vib + drift + noise)
                temp = float(m.normal_temperature_max) * random.uniform(0.5, 0.8) + (drift * 2 if degrading else 0)
                press = float(m.normal_pressure_max) * random.uniform(0.5, 0.85)
                rpm = random.randint(900, 1800)

                is_anom, score = score_reading(m, vib, temp, press, rpm)
                r = SensorReading.objects.create(
                    machine=m, vibration_mm_s=Decimal(str(round(vib, 3))), temperature_c=Decimal(str(round(temp, 2))),
                    pressure_bar=Decimal(str(round(press, 2))), rpm=rpm, is_anomaly=is_anom, anomaly_score=score)
                SensorReading.objects.filter(pk=r.pk).update(recorded_at=t)
                n_readings += 1

        if not WorkOrder.objects.exists():
            WorkOrder.objects.create(machine=machines[0], title="Replace compressor air filter", priority=WorkOrder.MEDIUM,
                                      created_by=manager, assigned_to=engineer)
            WorkOrder.objects.create(machine=machines[-1], title="Investigate rising vibration trend", priority=WorkOrder.HIGH,
                                      created_by=manager, assigned_to=engineer, is_ai_generated=True)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(machines)} machines, {n_readings} sensor readings, {WorkOrder.objects.count()} work orders."))
        self.stdout.write("Logins (password Demo@12345):")
        self.stdout.write("  admin     admin@factorypulse.io")
        self.stdout.write("  manager   manager@factorypulse.io")
        self.stdout.write("  engineer  engineer@factorypulse.io")
        self.stdout.write("  operator  operator@factorypulse.io")
