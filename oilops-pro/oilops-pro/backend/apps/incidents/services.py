from apps.accounts.models import Role
from apps.notifications.services import notify, users_with_roles
from apps.workorders.services import create_system_work_order

CRITICAL_TYPES = {"FIRE", "EXPLOSION", "GAS_LEAK"}


def handle_new_incident(incident):
    severe = incident.severity in ("MAJOR", "CATASTROPHIC") or incident.incident_type in CRITICAL_TYPES
    notify(users_with_roles(Role.SAFETY_OFFICER, Role.PLANT_MANAGER), "INCIDENT",
           f"{incident.get_incident_type_display()}: {incident.title}",
           f"{incident.number} at {incident.plant.name} - severity {incident.get_severity_display()}.",
           f"/incidents/{incident.pk}", severity="critical" if severe else "warning", email=severe)
    eq = incident.equipment
    if eq and incident.incident_type == "EQUIPMENT_FAILURE":
        if eq.status != "FAULTY":
            eq.status = "FAULTY"
            eq.save(update_fields=["status", "updated_at"])
        create_system_work_order(eq, f"Repair after failure: {eq.name}", incident.description,
                                 wo_type="EMERGENCY" if severe else "CORRECTIVE",
                                 priority="CRITICAL" if severe else "HIGH", incident=incident)
