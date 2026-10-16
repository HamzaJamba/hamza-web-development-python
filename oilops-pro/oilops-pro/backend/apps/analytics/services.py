from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Avg, Count, F, Q, Sum
from django.utils import timezone

from apps.equipment.models import Equipment
from apps.incidents.models import Incident
from apps.inventory.models import Item, StockMovement
from apps.monitoring.models import Alert
from apps.workorders.models import WorkOrder


def month_keys(n):
    """Last n months as ['YYYY-MM', ...] oldest first."""
    today = date.today().replace(day=1)
    keys = []
    for i in range(n - 1, -1, -1):
        y, m = today.year, today.month - i
        while m <= 0:
            y, m = y - 1, m + 12
        keys.append(f"{y}-{m:02d}")
    return keys


def mkey(dt):
    return f"{dt.year}-{dt.month:02d}"


def month_start(n):
    return date.fromisoformat(month_keys(n)[0] + "-01")


def f(x):
    return float(x or 0)


def overview(plant=None):
    eq = Equipment.objects.exclude(status="DECOMMISSIONED")
    wo = WorkOrder.objects.filter(status__in=WorkOrder.OPEN_STATUSES)
    inc = Incident.objects.all()
    alerts = Alert.objects.filter(status__in=["OPEN", "ACKNOWLEDGED"])
    if plant:
        eq, wo = eq.filter(plant=plant), wo.filter(equipment__plant=plant)
        inc, alerts = inc.filter(plant=plant), alerts.filter(equipment__plant=plant)
    total = eq.count()
    operational = eq.filter(status="OPERATIONAL").count()
    since30 = timezone.now() - timedelta(days=30)
    return {
        "equipment_total": total,
        "equipment_operational": operational,
        "availability_pct": round(operational / total * 100, 1) if total else 0,
        "avg_health": round(eq.aggregate(a=Avg("health_score"))["a"] or 0, 1),
        "open_work_orders": wo.count(),
        "overdue_work_orders": wo.filter(deadline__lt=timezone.now()).count(),
        "critical_work_orders": wo.filter(priority="CRITICAL").count(),
        "open_alerts": alerts.count(),
        "critical_alerts": alerts.filter(severity="CRITICAL").count(),
        "open_incidents": inc.exclude(status__in=["RESOLVED", "CLOSED"]).count(),
        "incidents_30d": inc.filter(occurred_at__gte=since30).count(),
        "low_stock_items": Item.objects.filter(is_active=True, quantity__lte=F("reorder_level")).count(),
        "maintenance_overdue": eq.filter(next_maintenance_date__lt=date.today()).count(),
    }


def equipment_health(plant=None):
    eq = Equipment.objects.exclude(status="DECOMMISSIONED")
    if plant:
        eq = eq.filter(plant=plant)
    buckets = {"healthy (80-100)": eq.filter(health_score__gte=80).count(),
               "degraded (50-79)": eq.filter(health_score__gte=50, health_score__lt=80).count(),
               "poor (<50)": eq.filter(health_score__lt=50).count()}
    return {
        "status_distribution": list(eq.values("status").annotate(count=Count("id")).order_by("status")),
        "health_buckets": [{"label": k, "count": v} for k, v in buckets.items()],
        "by_category": [{"category": r["category"], "avg_health": round(r["a"], 1), "count": r["c"]}
                        for r in eq.values("category").annotate(a=Avg("health_score"), c=Count("id")).order_by("category")],
        "lowest": list(eq.order_by("health_score", "name")[:8].values("id", "name", "serial_number", "health_score", "status")),
    }


def downtime(months=6, plant=None):
    keys = month_keys(months)
    start = month_start(months)
    series = {k: {"month": k, "incident_hours": 0.0, "work_order_hours": 0.0} for k in keys}
    inc = Incident.objects.filter(occurred_at__date__gte=start)
    wos = WorkOrder.objects.filter(status="COMPLETED", completed_at__date__gte=start)
    if plant:
        inc, wos = inc.filter(plant=plant), wos.filter(equipment__plant=plant)
    for i in inc:
        k = mkey(i.occurred_at)
        if k in series:
            series[k]["incident_hours"] += f(i.downtime_hours)
    for w in wos:
        k = mkey(w.completed_at)
        if k in series:
            series[k]["work_order_hours"] += f(w.downtime_hours)
    top = (wos.values("equipment__name").annotate(h=Sum("downtime_hours")).order_by("-h")[:8])
    return {"monthly": list(series.values()),
            "total_hours": round(sum(s["incident_hours"] + s["work_order_hours"] for s in series.values()), 1),
            "top_equipment": [{"equipment": r["equipment__name"], "hours": f(r["h"])} for r in top]}


def maintenance_cost(months=6, plant=None):
    keys = month_keys(months)
    series = {k: {"month": k, "PREVENTIVE": 0.0, "CORRECTIVE": 0.0, "EMERGENCY": 0.0} for k in keys}
    wos = (WorkOrder.objects.filter(status="COMPLETED", completed_at__date__gte=month_start(months))
           .prefetch_related("parts"))
    if plant:
        wos = wos.filter(equipment__plant=plant)
    by_type = defaultdict(float)
    for w in wos:
        k = mkey(w.completed_at)
        if k in series:
            c = f(w.total_cost)
            series[k][w.wo_type] += c
            by_type[w.wo_type] += c
    return {"monthly": [{**s, **{t: round(s[t], 2) for t in ("PREVENTIVE", "CORRECTIVE", "EMERGENCY")}} for s in series.values()],
            "by_type": [{"type": t, "cost": round(v, 2)} for t, v in by_type.items()],
            "total": round(sum(by_type.values()), 2)}


def incident_stats(months=6, plant=None):
    keys = month_keys(months)
    types = [c[0] for c in Incident.Type.choices]
    series = {k: {"month": k, **{t: 0 for t in types}} for k in keys}
    qs = Incident.objects.filter(occurred_at__date__gte=month_start(months))
    if plant:
        qs = qs.filter(plant=plant)
    for i in qs:
        k = mkey(i.occurred_at)
        if k in series:
            series[k][i.incident_type] += 1
    return {"monthly": list(series.values()),
            "by_severity": list(qs.values("severity").annotate(count=Count("id"))),
            "by_type": list(qs.values("incident_type").annotate(count=Count("id"))),
            "total": qs.count(), "injuries": qs.aggregate(s=Sum("injuries"))["s"] or 0,
            "estimated_loss": f(qs.aggregate(s=Sum("estimated_loss"))["s"])}


def inventory_usage(months=6):
    keys = month_keys(months)
    cats = [c[0] for c in Item.Category.choices]
    series = {k: {"month": k, **{c: 0.0 for c in cats}} for k in keys}
    mv = StockMovement.objects.filter(movement_type="OUT", created_at__date__gte=month_start(months)).select_related("item")
    for m in mv:
        k = mkey(m.created_at)
        if k in series:
            series[k][m.item.category] += f(m.quantity)
    top = (mv.values("item__name", "item__unit").annotate(q=Sum("quantity")).order_by("-q")[:8])
    value = (Item.objects.filter(is_active=True).values("category")
             .annotate(v=Sum(F("quantity") * F("unit_cost"))))
    return {"monthly": list(series.values()),
            "top_items": [{"item": r["item__name"], "unit": r["item__unit"], "quantity": f(r["q"])} for r in top],
            "stock_value": [{"category": r["category"], "value": f(r["v"])} for r in value]}


def employee_performance(days=90, plant=None):
    since = timezone.now() - timedelta(days=days)
    wos = (WorkOrder.objects.filter(status="COMPLETED", completed_at__gte=since)
           .prefetch_related("technicians").select_related("engineer"))
    if plant:
        wos = wos.filter(equipment__plant=plant)
    stats = defaultdict(lambda: {"completed": 0, "on_time": 0, "hours": 0.0})
    names = {}
    for w in wos:
        people = list(w.technicians.all()) + ([w.engineer] if w.engineer else [])
        for u in people:
            names[u.pk] = (u.full_name, u.role)
            s = stats[u.pk]
            s["completed"] += 1
            s["hours"] += f(w.labor_hours)
            if not w.deadline or w.completed_at <= w.deadline:
                s["on_time"] += 1
    rows = [{"user_id": uid, "name": names[uid][0], "role": names[uid][1], "completed": s["completed"],
             "on_time_pct": round(s["on_time"] / s["completed"] * 100, 1), "labor_hours": round(s["hours"], 1)}
            for uid, s in stats.items()]
    return sorted(rows, key=lambda r: (-r["completed"], -r["on_time_pct"]))
