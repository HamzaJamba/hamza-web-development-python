from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.accounts.models import Role
from apps.notifications.models import Notification
from apps.notifications.services import notify, users_with_roles

from .models import Certification


@shared_task
def check_certification_expiry():
    """Notify HR / safety officers about certifications expiring soon (once per cert)."""
    horizon = timezone.localdate() + timedelta(days=settings.CERT_EXPIRY_WARNING_DAYS)
    certs = Certification.objects.filter(expires_on__isnull=False, expires_on__lte=horizon).select_related("employee")
    recipients = users_with_roles(Role.HR, Role.SAFETY_OFFICER)
    sent = 0
    for c in certs:
        title = f"Certification expiring: {c.name} ({c.employee.full_name})"
        if Notification.objects.filter(kind="CERTIFICATION", title=title).exists():
            continue
        notify(recipients, "CERTIFICATION", title, f"Expires on {c.expires_on}.", "/employees",
               severity="critical" if c.is_expired else "warning")
        sent += 1
    return sent
