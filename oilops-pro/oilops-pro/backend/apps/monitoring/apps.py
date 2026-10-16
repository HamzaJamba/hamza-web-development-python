from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    def ready(self):
        from . import schema  # noqa: F401

    name = "apps.monitoring"
    default_auto_field = "django.db.models.BigAutoField"
