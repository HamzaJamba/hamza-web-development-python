from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/plant/$", consumers.PlantOverviewConsumer.as_asgi()),
    re_path(r"ws/machine/(?P<machine_id>[0-9a-f-]+)/$", consumers.MachineConsumer.as_asgi()),
]
