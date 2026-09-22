"""
Drop-in mixin for DRF ModelViewSets that logs every create/update/delete
to the AuditLog table, capturing who did it and from where.
"""
from .models import AuditLog


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class AuditLogMixin:
    def _log(self, action, instance):
        request = self.request
        user = request.user if request.user.is_authenticated else None
        AuditLog.objects.create(
            user=user,
            action=action,
            model_name=instance.__class__.__name__,
            object_id=str(instance.pk),
            object_repr=str(instance)[:255],
            ip_address=_client_ip(request),
            path=request.path,
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        self._log(AuditLog.CREATE, instance)
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        self._log(AuditLog.UPDATE, instance)
        return instance

    def perform_destroy(self, instance):
        self._log(AuditLog.DELETE, instance)
        instance.delete()
