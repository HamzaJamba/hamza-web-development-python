from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import Role
from apps.inventory.models import Item
from apps.inventory.services import adjust_stock
from apps.notifications.services import notify, users_with_roles

from .models import SparePartUsage, WorkOrder

S = WorkOrder.Status
TRANSITIONS = {
    "start": ({S.OPEN, S.ASSIGNED, S.ON_HOLD}, S.IN_PROGRESS),
    "hold": ({S.IN_PROGRESS}, S.ON_HOLD),
    "complete": ({S.IN_PROGRESS}, S.COMPLETED),
    "cancel": ({S.OPEN, S.ASSIGNED, S.ON_HOLD, S.IN_PROGRESS}, S.CANCELLED),
}
ELEVATED = {Role.ADMIN, Role.PLANT_MANAGER, Role.ENGINEER}


def _check(wo, action):
    allowed, _ = TRANSITIONS[action]
    if wo.status not in allowed:
        raise ValidationError({"status": f"Cannot {action} a work order that is {wo.get_status_display().lower()}."})


def _check_assignee(wo, user):
    if user.role in ELEVATED or user.is_superuser:
        return
    if not wo.technicians.filter(pk=user.pk).exists():
        raise PermissionDenied("You are not assigned to this work order.")


@transaction.atomic
def assign(wo, engineer=None, technicians=None, by=None):
    if wo.status in (S.COMPLETED, S.CANCELLED):
        raise ValidationError({"status": "Closed work orders cannot be reassigned."})
    if engineer is not None:
        wo.engineer = engineer
    if technicians is not None:
        wo.technicians.set(technicians)
    if wo.status == S.OPEN and (wo.engineer_id or wo.technicians.exists()):
        wo.status = S.ASSIGNED
    wo.save()
    people = [u for u in [wo.engineer, *wo.technicians.all()] if u]
    notify(people, "WORK_ORDER", f"Assigned: {wo.number}", wo.title, f"/work-orders/{wo.pk}",
           severity="warning" if wo.priority in ("HIGH", "CRITICAL") else "info", email=wo.priority == "CRITICAL")
    return wo


@transaction.atomic
def start(wo, user):
    _check(wo, "start")
    _check_assignee(wo, user)
    wo.status = S.IN_PROGRESS
    wo.started_at = wo.started_at or timezone.now()
    wo.save(update_fields=["status", "started_at", "updated_at"])
    eq = wo.equipment
    if eq.status in ("OPERATIONAL", "FAULTY"):
        eq.status = "MAINTENANCE"
        eq.save(update_fields=["status", "updated_at"])
    return wo


def hold(wo, user, reason=""):
    _check(wo, "hold")
    _check_assignee(wo, user)
    wo.status = S.ON_HOLD
    if reason:
        wo.completion_notes = f"{wo.completion_notes}\n[On hold] {reason}".strip()
    wo.save(update_fields=["status", "completion_notes", "updated_at"])
    return wo


@transaction.atomic
def complete(wo, user, notes, labor_hours=None, downtime_hours=None):
    _check(wo, "complete")
    _check_assignee(wo, user)
    if not (notes or "").strip():
        raise ValidationError({"completion_notes": "Completion notes are required."})
    today = timezone.localdate()
    wo.status = S.COMPLETED
    wo.completed_at = timezone.now()
    wo.completion_notes = notes.strip()
    if labor_hours is not None:
        wo.labor_hours = labor_hours
    if downtime_hours is not None:
        wo.downtime_hours = downtime_hours
    wo.save()
    eq = wo.equipment
    eq.last_service_date = today
    if eq.status in ("MAINTENANCE", "FAULTY"):
        eq.status = "OPERATIONAL"
    if wo.schedule_id:
        wo.schedule.mark_performed(today)  # also syncs equipment.next_maintenance_date
        eq.refresh_from_db(fields=["next_maintenance_date"])
    elif wo.wo_type == WorkOrder.Type.PREVENTIVE:
        eq.next_maintenance_date = today + timedelta(days=90)
    eq.save()
    from apps.monitoring.services import recompute_health
    recompute_health(eq)
    notify([u for u in {wo.created_by, wo.engineer} if u], "WORK_ORDER", f"Completed: {wo.number}",
           wo.title, f"/work-orders/{wo.pk}")
    return wo


@transaction.atomic
def cancel(wo, user, reason=""):
    _check(wo, "cancel")
    wo.status = S.CANCELLED
    wo.completion_notes = f"{wo.completion_notes}\n[Cancelled] {reason}".strip()
    wo.save(update_fields=["status", "completion_notes", "updated_at"])
    return wo


@transaction.atomic
def add_part(wo, item_id, quantity, user):
    if wo.status in (S.COMPLETED, S.CANCELLED):
        raise ValidationError({"status": "Cannot add parts to a closed work order."})
    _check_assignee(wo, user)
    item = Item.objects.get(pk=item_id)
    adjust_stock(item.pk, "OUT", Decimal(quantity), user, reference=wo.number, notes=f"Used on {wo.title}"[:255])
    return SparePartUsage.objects.create(work_order=wo, item=item, quantity=quantity, unit_cost=item.unit_cost, used_by=user)


def create_system_work_order(equipment, title, description, wo_type="EMERGENCY", priority="CRITICAL", incident=None, hours=4):
    """Used by monitoring/incidents. Skips if an open emergency/corrective order already exists for the equipment."""
    existing = WorkOrder.objects.filter(equipment=equipment, wo_type__in=["EMERGENCY", "CORRECTIVE"],
                                        status__in=WorkOrder.OPEN_STATUSES).first()
    if existing:
        return existing, False
    wo = WorkOrder.objects.create(
        title=title, description=description, equipment=equipment, wo_type=wo_type, priority=priority,
        incident=incident, deadline=timezone.now() + timedelta(hours=hours))
    notify(users_with_roles(Role.PLANT_MANAGER, Role.ENGINEER), "WORK_ORDER", f"{wo.number} auto-created",
           title, f"/work-orders/{wo.pk}", severity="critical", email=priority == "CRITICAL")
    return wo, True
