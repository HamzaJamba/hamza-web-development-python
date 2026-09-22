from django.contrib import admin
from .models import Shipment, ShipmentAttachment, ShipmentStatusHistory

admin.site.register(Shipment)
admin.site.register(ShipmentAttachment)
admin.site.register(ShipmentStatusHistory)
