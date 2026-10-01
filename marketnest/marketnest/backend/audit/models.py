import uuid
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ACTION_CHOICES = [(CREATE, "Create"), (UPDATE, "Update"), (DELETE, "Delete")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs"
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    object_repr = models.CharField(max_length=255, blank=True)
    changes = models.JSONField(blank=True, null=True, help_text="Field-level diff, where available")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    path = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["model_name", "object_id"])]

    def __str__(self):
        return f"{self.action} {self.model_name}({self.object_id}) by {self.user_id} @ {self.timestamp}"
