from datetime import date, timedelta

from django.db.models import Count, Sum
from django.utils import timezone

from apps.analytics import services as an
from apps.equipment.models import Equipment
from apps.incidents.models import Incident
from apps.workorders.models import WorkOrder


def _range(p):
    to = date.fromisoformat(p["date_to"]) if p.get("date_to") else date.today()
    frm = date.fromisoformat(p["date_from"]) if p.get("date_from") else to - timedelta(days=90)
    return frm, to


def maintenance_report(p):
    frm, to = _range(p)
    qs = (WorkOrder.objects.filter(created_at__date__range=(frm, to)).select_related("equipment", "engineer")
          .prefetch_related("parts"))
    if p.get("plant"):
        qs = qs.filter(equipment__plant=p["plant"])
    rows = [[w.number, w.title, w.equipment.name, w.get_wo_type_display(), w.get_priority_display(), w.get_status_display(),
             w.engineer.full_name if w.engineer else "-", f"{w.created_at:%Y-%m-%d}",
             f"{w.completed_at:%Y-%m-%d}" if w.completed_at else "-", float(w.downtime_hours), round(float(w.total_cost), 2)]
            for w in qs]
    total = sum(r[-1] for r in rows)
    return {"title": "Maintenance report", "subtitle": f"{frm} to {to}",
            "columns": ["WO #", "Title", "Equipment", "Type", "Priority", "Status", "Engineer", "Created", "Completed", "Downtime h", "Cost"],
            "rows": rows, "summary": {"Work orders": len(rows), "Total cost": round(total, 2)}}


def incident_report(p):
    frm, to = _range(p)
    qs = Incident.objects.filter(occurred_at__date__range=(frm, to)).select_related("plant", "equipment")
    if p.get("plant"):
        qs = qs.filter(plant=p["plant"])
    rows = [[i.number, i.title, i.get_incident_type_display(), i.get_severity_display(), i.get_status_display(), i.plant.name,
             i.equipment.name if i.equipment else "-", f"{i.occurred_at:%Y-%m-%d %H:%M}", i.injuries, float(i.downtime_hours),
             float(i.estimated_loss)] for i in qs]
    return {"title": "Incident report", "subtitle": f"{frm} to {to}",
            "columns": ["Incident #", "Title", "Type", "Severity", "Status", "Plant", "Equipment", "Occurred", "Injuries", "Downtime h", "Loss"],
            "rows": rows, "summary": {"Incidents": len(rows), "Injuries": sum(r[8] for r in rows),
                                      "Estimated loss": round(sum(r[10] for r in rows), 2)}}


def equipment_report(p):
    qs = Equipment.objects.select_related("plant")
    if p.get("plant"):
        qs = qs.filter(plant=p["plant"])
    rows = [[e.serial_number, e.name, e.get_category_display(), e.plant.name, e.get_status_display(), e.health_score,
             str(e.last_service_date or "-"), str(e.next_maintenance_date or "-"), str(e.warranty_expiry or "-"),
             "Yes" if e.warranty_active else "No"] for e in qs]
    return {"title": "Equipment report", "subtitle": f"As of {date.today()}",
            "columns": ["Serial", "Name", "Category", "Plant", "Status", "Health", "Last service", "Next maintenance", "Warranty to", "In warranty"],
            "rows": rows, "summary": {"Equipment": len(rows),
                                      "Avg health": round(sum(r[5] for r in rows) / len(rows), 1) if rows else 0}}


def monthly_performance(p):
    month = p.get("month") or date.today().strftime("%Y-%m")
    y, m = map(int, month.split("-"))
    start = date(y, m, 1)
    end = date(y + (m == 12), (m % 12) + 1, 1)
    wos = WorkOrder.objects.filter(created_at__date__gte=start, created_at__date__lt=end)
    done = WorkOrder.objects.filter(completed_at__date__gte=start, completed_at__date__lt=end, status="COMPLETED").prefetch_related("parts")
    inc = Incident.objects.filter(occurred_at__date__gte=start, occurred_at__date__lt=end)
    ov = an.overview()
    on_time = sum(1 for w in done if not w.deadline or w.completed_at <= w.deadline)
    rows = [
        ["Work orders created", wos.count()],
        ["Work orders completed", done.count()],
        ["Completed on time (%)", round(on_time / done.count() * 100, 1) if done.count() else 0],
        ["Maintenance cost", round(sum(float(w.total_cost) for w in done), 2)],
        ["Downtime hours (work orders)", float(done.aggregate(s=Sum("downtime_hours"))["s"] or 0)],
        ["Incidents", inc.count()],
        ["Injuries", inc.aggregate(s=Sum("injuries"))["s"] or 0],
        ["Incident downtime hours", float(inc.aggregate(s=Sum("downtime_hours"))["s"] or 0)],
        ["Equipment availability now (%)", ov["availability_pct"]],
        ["Average equipment health now", ov["avg_health"]],
        ["Low-stock items now", ov["low_stock_items"]],
    ]
    return {"title": "Monthly performance report", "subtitle": month, "columns": ["KPI", "Value"], "rows": rows,
            "summary": {}}


REPORTS = {"maintenance": maintenance_report, "incidents": incident_report, "equipment": equipment_report,
           "monthly-performance": monthly_performance}
