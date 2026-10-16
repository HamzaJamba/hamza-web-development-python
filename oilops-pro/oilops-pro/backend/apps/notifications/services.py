from django.contrib.auth import get_user_model

from .models import Notification
from .tasks import send_email_notification


def users_with_roles(*roles):
    User = get_user_model()
    return User.objects.filter(is_active=True, role__in=list(roles) + ["ADMIN"])


def notify(users, kind, title, message="", link="", severity="info", email=False):
    """In-app notification for every user, optionally followed by an email (async)."""
    users = list({u.pk: u for u in users}.values())
    if not users:
        return []
    created = Notification.objects.bulk_create(
        [Notification(user=u, kind=kind, title=title, message=message, link=link, severity=severity) for u in users]
    )
    if email:
        send_email_notification.delay([u.email for u in users], f"[OilOps] {title}", message or title)
    return created
