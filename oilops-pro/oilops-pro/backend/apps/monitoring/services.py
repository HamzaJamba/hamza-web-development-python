import logging

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from apps.accounts.models import Role
from apps.notifications.services import notify, users_with_roles

from .models import METRIC_UNITS, Alert, SensorReading, Threshold

log = logging.getLogger(__name__)
SEVERITY_RANK = {"WARNING": 1, "CRITICAL": 2}
OPEN = ("OPEN", "ACKNOWLEDGED")


def applicable_thresholds(equipment, metric):
    specific = Threshold.objects.filter(is_active=True, metric=metric, equipment=equipment)
    if specific.exists():
        return list(specific)
    return list(Threshold.objects.filter(is_active=True, metric=metric, equipment__isnull=True)
                .filter(Q(category=equipment.category) | Q(category="")))


def recompute_health(equipment):
    """100 - 25 per open critical alert - 8 per open warning - 10 when maintenance is overdue."""
    qs = Alert.objects.filter(equipment=equipment, status__in=OPEN)
    score = 100 - 25 * qs.filter(severity="CRITICAL").count() - 8 * qs.filter(severity="WARNING").count()
    if equipment.maintenance_overdue:
        score -= 10
    score = max(0, min(100, score))
    if score != equipment.health_score:
        equipment.health_score = score
        equipment.save(update_fields=["health_score", "updated_at"])
    return score


def ingest_reading(equipment, metric, value, recorded_at=None):
    """Store a reading, evaluate thresholds, raise / escalate / auto-resolve alerts."""
    reading = SensorReading.objects.create(equipment=equipment, metric=metric, value=value,
                                           recorded_at=recorded_at or timezone.now())
    breached = [t for t in applicable_thresholds(equipment, metric) if t.breached_by(value)]
    open_alert = Alert.objects.filter(equipment=equipment, metric=metric, status__in=OPEN).first()

    if not breached:
        if open_alert:
            open_alert.status = Alert.Status.RESOLVED
            open_alert.resolved_at = timezone.now()
            open_alert.save()
            recompute_health(equipment)
        return reading, None

    worst = max(breached, key=lambda t: SEVERITY_RANK[t.severity])
    unit = METRIC_UNITS.get(metric, "")
    message = f"{equipment.name}: {metric.replace('_', ' ').title()} {value:g}{unit} outside limits"
    if open_alert:
        escalated = SEVERITY_RANK[worst.severity] > SEVERITY_RANK[open_alert.severity]
        open_alert.occurrence_count += 1
        open_alert.value = value
        open_alert.threshold = worst
        if escalated:
            open_alert.severity = worst.severity
            open_alert.message = message
        open_alert.save()
        alert, is_new = open_alert, escalated
    else:
        alert = Alert.objects.create(equipment=equipment, metric=metric, severity=worst.severity, value=value,
                                     threshold=worst, message=message)
        is_new = True

    if is_new:
        recompute_health(equipment)
        critical = alert.severity == "CRITICAL"
        notify(users_with_roles(Role.ENGINEER, Role.PLANT_MANAGER) if critical else users_with_roles(Role.ENGINEER),
               "ALERT", message, f"Value {value:g}{unit} on {equipment.serial_number}.", f"/monitoring",
               severity="critical" if critical else "warning", email=critical)
        if critical and settings.AUTO_WORK_ORDER_ON_CRITICAL_ALERT:
            from apps.workorders.services import create_system_work_order
            create_system_work_order(equipment, f"Critical alert: {message}", message, hours=4)
    return reading, alert
