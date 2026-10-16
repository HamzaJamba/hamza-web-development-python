"""Populate a realistic demo dataset: python manage.py seed_demo [--reset]"""
import random
from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.employees.models import Certification, Department, Employee, Position, SalaryGrade, Shift, TrainingRecord
from apps.equipment.models import Equipment
from apps.incidents.models import Incident
from apps.inventory.models import Item
from apps.inventory.services import adjust_stock
from apps.maintenance.models import MaintenanceSchedule
from apps.monitoring.models import SensorReading, Threshold
from apps.monitoring.services import recompute_health
from apps.plants.models import Pipeline, Plant, StorageTank
from apps.workorders.models import SparePartUsage, WorkOrder

PASSWORD = "OilOps@2026!"
USERS = [
    ("admin@oilops.com", "Ayesha", "Khan", "ADMIN"), ("manager@oilops.com", "Bilal", "Ahmed", "PLANT_MANAGER"),
    ("engineer@oilops.com", "Sara", "Malik", "ENGINEER"), ("engineer2@oilops.com", "Omar", "Farooq", "ENGINEER"),
    ("tech1@oilops.com", "Usman", "Raza", "TECHNICIAN"), ("tech2@oilops.com", "Hassan", "Ali", "TECHNICIAN"),
    ("tech3@oilops.com", "Zain", "Sheikh", "TECHNICIAN"), ("safety@oilops.com", "Maryam", "Siddiqui", "SAFETY_OFFICER"),
    ("store@oilops.com", "Imran", "Butt", "STORE_KEEPER"), ("hr@oilops.com", "Nida", "Hussain", "HR"),
    ("viewer@oilops.com", "Guest", "Viewer", "VIEWER"),
]
PLANTS = [
    ("KCR", "Karachi Coastal Refinery", "REFINERY", "Karachi", 24.8465, 67.0011, 120000),
    ("DGP", "Daharki Gas Processing Plant", "PLANT", "Daharki", 28.0003, 69.6784, 85000),
    ("PQT", "Port Qasim Storage Terminal", "TERMINAL", "Karachi", 24.7774, 67.3361, 60000),
    ("AHR", "Attock Highland Refinery", "REFINERY", "Rawalpindi", 33.5651, 73.0169, 45000),
    ("LRF", "Lahore Ring Road Fuel Station", "GAS_STATION", "Lahore", 31.5204, 74.3587, 0),
]
EQUIP = [  # name, category, manufacturer, criticality
    ("Crude Feed Pump P-101", "PUMP", "Flowserve", "CRITICAL"), ("Booster Pump P-102", "PUMP", "Sulzer", "HIGH"),
    ("Gas Compressor C-201", "COMPRESSOR", "Atlas Copco", "CRITICAL"), ("Recycle Compressor C-202", "COMPRESSOR", "Ingersoll Rand", "HIGH"),
    ("Isolation Valve V-301", "VALVE", "Emerson", "MEDIUM"), ("Control Valve V-302", "VALVE", "Honeywell", "MEDIUM"),
    ("Standby Generator G-401", "GENERATOR", "Caterpillar", "HIGH"), ("Gas Turbine T-501", "TURBINE", "Siemens Energy", "CRITICAL"),
    ("Pressure Transmitter S-601", "SENSOR", "Yokogawa", "LOW"),
]
ITEMS = [
    ("SP-1001", "Mechanical seal kit", "SPARE_PART", "pcs", 24, 10, 180), ("SP-1002", "Bearing 6310", "SPARE_PART", "pcs", 8, 12, 45),
    ("SP-1003", "Gasket set DN150", "SPARE_PART", "sets", 40, 15, 22), ("SP-1004", "Pressure relief valve", "SPARE_PART", "pcs", 6, 4, 640),
    ("CH-2001", "Corrosion inhibitor", "CHEMICAL", "L", 800, 300, 6.5), ("CH-2002", "Demulsifier", "CHEMICAL", "L", 150, 200, 9.2),
    ("LB-3001", "Turbine oil ISO VG 32", "LUBRICANT", "L", 1200, 400, 4.8), ("LB-3002", "Compressor oil", "LUBRICANT", "L", 600, 250, 5.4),
    ("LB-3003", "Grease EP2", "LUBRICANT", "kg", 90, 40, 7.1), ("SF-4001", "Flame-resistant coverall", "SAFETY", "pcs", 55, 30, 38),
    ("SF-4002", "Gas detector H2S portable", "SAFETY", "pcs", 5, 6, 410), ("SF-4003", "Safety helmet", "SAFETY", "pcs", 120, 50, 12),
]
THRESHOLDS = [  # metric, min, max, severity
    ("TEMPERATURE", None, 95, "WARNING"), ("TEMPERATURE", None, 110, "CRITICAL"),
    ("PRESSURE", None, 55, "WARNING"), ("PRESSURE", None, 65, "CRITICAL"),
    ("VOLTAGE", 370, 430, "WARNING"), ("VOLTAGE", 350, 450, "CRITICAL"),
    ("VIBRATION", None, 4.5, "WARNING"), ("VIBRATION", None, 7, "CRITICAL"),
    ("OIL_LEVEL", 40, None, "WARNING"), ("OIL_LEVEL", 25, None, "CRITICAL"),
]


class Command(BaseCommand):
    help = "Seed demo data"

    def add_arguments(self, p):
        p.add_argument("--reset", action="store_true", help="delete existing domain data first")

    @transaction.atomic
    def handle(self, *a, **o):
        random.seed(7)
        if o["reset"]:
            for m in (WorkOrder, Incident, MaintenanceSchedule, Equipment, Item, StorageTank, Pipeline, Plant, Employee, Threshold):
                m.objects.all().delete()
        elif Plant.objects.exists():
            self.stdout.write("Data already present. Use --reset to rebuild.")
            return
        users = {}
        for email, fn, ln, role in USERS:
            u, _ = User.objects.get_or_create(email=email, defaults={"first_name": fn, "last_name": ln, "role": role,
                                                                     "is_staff": role == "ADMIN", "is_superuser": role == "ADMIN"})
            u.set_password(PASSWORD)
            u.save()
            users[email.split("@")[0]] = u
        # HR structure
        depts = {c: Department.objects.get_or_create(code=c, defaults={"name": n})[0]
                 for c, n in [("OPS", "Operations"), ("MNT", "Maintenance"), ("HSE", "Health, Safety & Environment"),
                              ("LOG", "Logistics & Stores"), ("HR", "Human Resources")]}
        pos = {t: Position.objects.get_or_create(title=t, department=depts[d])[0]
               for t, d in [("Plant Manager", "OPS"), ("Maintenance Engineer", "MNT"), ("Technician", "MNT"),
                            ("HSE Officer", "HSE"), ("Store Keeper", "LOG"), ("HR Officer", "HR")]}
        shifts = [Shift.objects.get_or_create(name=n, defaults={"start_time": s, "end_time": e})[0]
                  for n, s, e in [("Morning", time(6), time(14)), ("Evening", time(14), time(22)), ("Night", time(22), time(6))]]
        grades = [SalaryGrade.objects.get_or_create(code=c, defaults={"name": n, "min_salary": lo, "max_salary": hi})[0]
                  for c, n, lo, hi in [("G1", "Technician", 60000, 110000), ("G2", "Engineer", 120000, 220000), ("G3", "Management", 230000, 450000)]]
        # plants, tanks, pipelines
        plants = {}
        for code, name, kind, city, lat, lng, cap in PLANTS:
            plants[code] = Plant.objects.create(code=code, name=name, plant_type=kind, city=city, latitude=lat, longitude=lng,
                                                capacity_bpd=cap, manager=users["manager"], commissioned_on=date(2012, 1, 1))
        for code, prods in [("KCR", ["CRUDE", "DIESEL", "PETROL"]), ("PQT", ["CRUDE", "KEROSENE", "DIESEL"]), ("DGP", ["LPG", "NATURAL_GAS"]),
                            ("AHR", ["CRUDE", "PETROL"]), ("LRF", ["PETROL", "DIESEL"])]:
            for i, prod in enumerate(prods, 1):
                cap = Decimal(random.choice([500000, 1200000, 2500000])) if code != "LRF" else Decimal(60000)
                StorageTank.objects.create(plant=plants[code], tag=f"TK-{i:02d}", product=prod, capacity_litres=cap,
                                           current_level_litres=cap * Decimal(random.uniform(0.2, 0.92)).quantize(Decimal("0.01")),
                                           last_inspection=date.today() - timedelta(days=random.randint(20, 300)))
        for code, n, a, b, km, d in [("PL-01", "Port Qasim - Karachi Trunk Line", "PQT", "KCR", 38, 24), ("PL-02", "Daharki - Attock Gas Main", "DGP", "AHR", 920, 30),
                                     ("PL-03", "Attock - Lahore Product Line", "AHR", "LRF", 310, 16)]:
            Pipeline.objects.create(code=code, name=n, origin=plants[a], destination=plants[b], length_km=km, diameter_inch=d,
                                    max_pressure_bar=70, product="Crude oil" if code == "PL-01" else "Refined product")
        # employees
        emp_defs = [("manager", "Plant Manager", 2, "KCR"), ("engineer", "Maintenance Engineer", 1, "KCR"), ("engineer2", "Maintenance Engineer", 1, "DGP"),
                    ("tech1", "Technician", 0, "KCR"), ("tech2", "Technician", 1, "DGP"), ("tech3", "Technician", 2, "PQT"),
                    ("safety", "HSE Officer", 0, "KCR"), ("store", "Store Keeper", 0, "KCR"), ("hr", "HR Officer", 0, "KCR")]
        for i, (key, title, sh, pl) in enumerate(emp_defs, 1):
            u = users[key]
            p = pos[title]
            e = Employee.objects.create(user=u, employee_id=f"EMP{1000 + i}", first_name=u.first_name, last_name=u.last_name, email=u.email,
                                        department=p.department, position=p, shift=shifts[sh], plant=plants[pl],
                                        salary_grade=grades[2 if "Manager" in title else 1 if "Engineer" in title else 0],
                                        hire_date=date.today() - timedelta(days=random.randint(300, 3000)))
            TrainingRecord.objects.create(employee=e, title="H2S awareness & rescue", provider="PetroSafe Institute",
                                          completed_on=date.today() - timedelta(days=random.randint(30, 400)), hours=16, score=random.randint(78, 98))
            Certification.objects.create(employee=e, name="Confined space entry", issuer="OSHA Training", certificate_no=f"CSE-{i:04d}",
                                         issued_on=date.today() - timedelta(days=330), expires_on=date.today() + timedelta(days=random.choice([12, 25, 200, 400])))
        # thresholds (category-wide, "" = all categories)
        for metric, lo, hi, sev in THRESHOLDS:
            Threshold.objects.create(metric=metric, min_value=lo, max_value=hi, severity=sev)
        # equipment
        equipment = []
        n = 0
        for code in ("KCR", "DGP", "PQT", "AHR"):
            for name, cat, mfr, crit in EQUIP[: random.randint(6, 9)]:
                n += 1
                purchase = date.today() - timedelta(days=random.randint(200, 2400))
                last = date.today() - timedelta(days=random.randint(10, 150))
                equipment.append(Equipment.objects.create(
                    plant=plants[code], name=name, category=cat, manufacturer=mfr, model_number=f"{mfr[:3].upper()}-{random.randint(100, 999)}",
                    serial_number=f"SN-{code}-{n:04d}", criticality=crit, purchase_date=purchase, purchase_cost=random.randint(8, 400) * 1000,
                    warranty_expiry=purchase + timedelta(days=365 * random.choice([1, 2, 3, 5])), last_service_date=last))
        eng = [users["engineer"], users["engineer2"]]
        for eq in equipment:
            if eq.category in ("SENSOR", "VALVE") and random.random() < 0.5:
                continue
            MaintenanceSchedule.objects.create(
                equipment=eq, title=random.choice(["Quarterly inspection & lubrication", "Vibration analysis & alignment", "Calibration & functional test"]),
                interval_days=random.choice([30, 60, 90, 180]), last_performed=eq.last_service_date, estimated_hours=random.choice([2, 4, 6, 8]),
                assigned_engineer=random.choice(eng),
                next_due=date.today() + timedelta(days=random.randint(-10, 80)))
        # inventory
        store = users["store"]
        items = []
        for sku, name, cat, unit, qty, rl, cost in ITEMS:
            it = Item.objects.create(sku=sku, name=name, category=cat, unit=unit, reorder_level=rl, unit_cost=cost, plant=plants["KCR"],
                                     supplier=random.choice(["Gulf Industrial Supply", "Indus Petro Parts", "Karakoram Chemicals"]),
                                     location=f"Bin {random.choice('ABCD')}-{random.randint(1, 20)}")
            adjust_stock(it.pk, "IN", Decimal(qty) + Decimal(random.randint(20, 80)), store, "OPENING", "Opening balance")
            items.append(it)
        # historical work orders (spread across the last 6 months for analytics)
        techs = [users["tech1"], users["tech2"], users["tech3"]]
        now = timezone.now()
        parts = [i for i in items if i.category == "SPARE_PART"]
        for k in range(46):
            eq = random.choice(equipment)
            kind = random.choices(["PREVENTIVE", "CORRECTIVE", "EMERGENCY"], [55, 35, 10])[0]
            done = random.random() < 0.82
            created = now - timedelta(days=random.randint(2, 175) if done else random.randint(1, 9))
            deadline = created + timedelta(days=random.randint(2, 10)) if done else now + timedelta(days=random.randint(-2, 8))
            wo = WorkOrder.objects.create(
                title=f"{kind.title()} - {eq.name}", description="Seeded work order.", equipment=eq, wo_type=kind,
                priority="CRITICAL" if kind == "EMERGENCY" else random.choice(["LOW", "MEDIUM", "HIGH"]), created_by=users["manager"],
                engineer=random.choice(eng), deadline=deadline,
                status="COMPLETED" if done else random.choice(["OPEN", "ASSIGNED", "IN_PROGRESS"]))
            wo.technicians.set(random.sample(techs, random.randint(1, 2)))
            fields = {"created_at": created}
            if done:
                finished = created + timedelta(days=random.randint(1, 11))
                fields.update(started_at=created + timedelta(hours=8), completed_at=finished, completion_notes="Work completed and tested.",
                              labor_hours=Decimal(random.choice([2, 3, 4, 6, 8, 12])),
                              downtime_hours=Decimal(0 if kind == "PREVENTIVE" else random.choice([2, 4, 8, 16])))
            WorkOrder.objects.filter(pk=wo.pk).update(**fields)
            if done and random.random() < 0.7:
                part = random.choice(parts)
                SparePartUsage.objects.create(work_order=wo, item=part, quantity=random.randint(1, 3), unit_cost=part.unit_cost, used_by=random.choice(techs))
        # history of stock consumption, one month at a time
        from apps.inventory.models import StockMovement
        for it in items:
            for _ in range(random.randint(4, 9)):
                it.refresh_from_db()
                q = min(random.randint(1, 6), int(it.quantity))
                if q < 1:
                    break
                m = adjust_stock(it.pk, "OUT", Decimal(q), store, f"ISSUE-{random.randint(1000, 9999)}", "Issued to maintenance")
                StockMovement.objects.filter(pk=m.pk).update(created_at=now - timedelta(days=random.randint(1, 170)))
        # leave a few items below reorder level so stock alerts are visible
        for sku, level in (("SP-1002", 5), ("CH-2002", 90), ("SF-4002", 2)):
            it = Item.objects.get(sku=sku)
            adjust_stock(it.pk, "ADJUST", Decimal(level), store, "COUNT", "Cycle count")
        # incidents
        types = list(Incident.Type.values)
        for k in range(14):
            when = now - timedelta(days=random.randint(1, 170))
            eq = random.choice(equipment)
            kind = random.choice(types)
            inc = Incident(title=f"{kind.replace('_', ' ').title()} reported near {eq.name}", incident_type=kind,
                           severity=random.choices(["MINOR", "MODERATE", "MAJOR", "CATASTROPHIC"], [50, 30, 17, 3])[0],
                           status=random.choice(["REPORTED", "INVESTIGATING", "RESOLVED", "CLOSED"]), plant=eq.plant,
                           equipment=eq if kind == "EQUIPMENT_FAILURE" else None, reported_by=users["safety"], occurred_at=when,
                           description="Seeded incident for demo purposes.", injuries=random.choice([0, 0, 0, 1, 2]),
                           downtime_hours=Decimal(random.choice([0, 2, 6, 12, 24])), estimated_loss=Decimal(random.randint(1, 90) * 1000))
            if inc.status in ("RESOLVED", "CLOSED"):
                inc.root_cause, inc.corrective_action = "Wear and inspection gap.", "Replaced component; inspection frequency raised."
            inc.save()
        # 24h telemetry history for charts (written directly, no alert noise)
        batch = []
        for eq in equipment:
            for metric, mean, noise in [("TEMPERATURE", 78, 4), ("PRESSURE", 42, 3), ("VIBRATION", 2.5, 0.5), ("OIL_LEVEL", 72, 3)]:
                for h in range(48):
                    batch.append(SensorReading(equipment=eq, metric=metric, value=round(random.gauss(mean, noise), 2),
                                               recorded_at=now - timedelta(minutes=30 * (48 - h))))
        SensorReading.objects.bulk_create(batch, batch_size=1000)
        for eq in equipment:
            recompute_health(eq)
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(USERS)} users, {len(plants)} plants, {len(equipment)} equipment, {len(items)} items. "
            f"Login: admin@oilops.com / {PASSWORD}"))
