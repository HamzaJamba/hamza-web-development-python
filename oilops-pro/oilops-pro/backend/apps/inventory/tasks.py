from datetime import timedelta

from celery import shared_task
from django.db.models import F
from django.utils import timezone

from apps.notifications.models import Notification

from .models import Item
from .services import notify_low_stock


@shared_task
def check_low_stock():
    """Daily sweep: remind about items that are still below reorder level (max once per 24h per item)."""
    since = timezone.now() - timedelta(hours=24)
    sent = 0
    for item in Item.objects.filter(is_active=True, quantity__lte=F("reorder_level")):
        if Notification.objects.filter(kind="LOW_STOCK", title=f"Low stock: {item.name}", created_at__gte=since).exists():
            continue
        notify_low_stock(item)
        sent += 1
    return sent
