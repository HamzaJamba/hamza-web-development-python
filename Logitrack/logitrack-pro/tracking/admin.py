from django.contrib import admin
from .models import GPSLog, IoTReading

admin.site.register(GPSLog)
admin.site.register(IoTReading)
