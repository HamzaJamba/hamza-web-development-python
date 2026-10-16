from datetime import date, timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.accounts.models import Role
from apps.notifications.models import Notification
from apps.notifications.services import notify, users_with_roles

from .models import MaintenanceSchedule


def _due_schedules():
    horizon = date.today() + timedelta(days=settings.MAINTENANCE_LEAD_DAYS)
    return (MaintenanceSchedule.objects.filter(is_active=True, next_due__lte=horizon)
            .exclude(equipment__status="DECOMMISSIONED").select_related("equipment", "assigned_engineer"))


@shared_task
def generate_due_work_orders():
    """Create preventive work orders for schedules inside the lead window (idempotent)."""
    from apps.workorders.models import WorkOrder

    created = 0
    for sch in _due_schedules().filter(auto_create_work_order=True):
        open_exists = WorkOrder.objects.filter(schedule=sch).exclude(status__in=["COMPLETED", "CANCELLED"]).exists()
        if open_exists:
            continue
        wo = WorkOrder.objects.create(
            title=f"Preventive: {sch.title}",
            description=sch.description or f"Scheduled maintenance for {sch.equipment.name}.",
            equipment=sch.equipment, schedule=sch, wo_type=WorkOrder.Type.PREVENTIVE,
            priority=WorkOrder.Priority.HIGH if sch.is_overdue else WorkOrder.Priority.MEDIUM,
            deadline=timezone.now().replace(hour=17, minute=0, second=0, microsecond=0) + timedelta(days=max((sch.next_due - date.today()).days, 0)),
            engineer=sch.assigned_engineer, estimated_hours=sch.estimated_hours,
            status=WorkOrder.Status.ASSIGNED if sch.assigned_engineer else WorkOrder.Status.OPEN)
        notify(users_with_roles(Role.PLANT_MANAGER, Role.ENGINEER), "WORK_ORDER", f"Work order {wo.number} created",
               f"Preventive maintenance for {sch.equipment.name} is due {sch.next_due}.", f"/work-orders/{wo.pk}")
        created += 1
    return created


@shared_task
def notify_maintenance_due():
    since = timezone.now() - timedelta(hours=24)
    sent = 0
    for sch in _due_schedules():
        title = f"Maintenance {'overdue' if sch.is_overdue else 'due'}: {sch.equipment.name}"
        if Notification.objects.filter(kind="MAINTENANCE_DUE", title=title, created_at__gte=since).exists():
            continue
        notify(users_with_roles(Role.PLANT_MANAGER, Role.ENGINEER), "MAINTENANCE_DUE", title,
               f"{sch.title} - due {sch.next_due}.", "/maintenance",
               severity="critical" if sch.is_overdue else "warning", email=sch.is_overdue)
        sent += 1
    return sent
