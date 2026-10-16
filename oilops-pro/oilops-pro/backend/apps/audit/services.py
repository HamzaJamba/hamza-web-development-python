import datetime
import decimal

from django.forms.models import model_to_dict

from .models import AuditLog


def _client_ip(request):
    if request is None:
        return None
    fwd = request.META.get("HTTP_X_FORWARDED_FOR")
    return (fwd.split(",")[0].strip() if fwd else request.META.get("REMOTE_ADDR")) or None


def _clean(value):
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, decimal.Decimal):
        return str(value)
    if hasattr(value, "name") and hasattr(value, "url"):  # FieldFile
        return value.name
    return value


def snapshot(instance):
    data = model_to_dict(instance)
    return {k: _clean(v if not isinstance(v, list) else [getattr(x, "pk", x) for x in v]) for k, v in data.items()}


def diff(before, after):
    return {k: {"from": before.get(k), "to": after.get(k)} for k in after if before.get(k) != after.get(k)}


def log_action(user, action, model, object_id="", object_repr="", changes=None, request=None):
    return AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action,
        model=model,
        object_id=str(object_id),
        object_repr=str(object_repr)[:255],
        changes=changes or {},
        ip_address=_client_ip(request),
        user_agent=(request.META.get("HTTP_USER_AGENT", "")[:255] if request is not None else ""),
    )
