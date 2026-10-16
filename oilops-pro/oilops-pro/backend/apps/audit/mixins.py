from .services import diff, log_action, snapshot


class AuditMixin:
    """Add to a ModelViewSet to write create/update/delete entries to the audit log."""

    def perform_create(self, serializer):
        super().perform_create(serializer)
        obj = serializer.instance
        log_action(self.request.user, "CREATE", obj.__class__.__name__, obj.pk, obj, snapshot(obj), self.request)

    def perform_update(self, serializer):
        before = snapshot(serializer.instance)
        super().perform_update(serializer)
        obj = serializer.instance
        changes = diff(before, snapshot(obj))
        if changes:
            log_action(self.request.user, "UPDATE", obj.__class__.__name__, obj.pk, obj, changes, self.request)

    def perform_destroy(self, instance):
        info = (instance.__class__.__name__, instance.pk, str(instance), snapshot(instance))
        super().perform_destroy(instance)
        log_action(self.request.user, "DELETE", info[0], info[1], info[2], info[3], self.request)
