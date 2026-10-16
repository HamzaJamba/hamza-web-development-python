from django.contrib import admin

from .models import Alert, SensorReading, Threshold

admin.site.register(Threshold)
admin.site.register(Alert)
admin.site.register(SensorReading)
