from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/tracking/fleet/$", consumers.FleetOverviewConsumer.as_asgi()),
    re_path(r"ws/tracking/(?P<vehicle_id>[0-9a-f-]+)/$", consumers.VehicleTrackingConsumer.as_asgi()),
]
