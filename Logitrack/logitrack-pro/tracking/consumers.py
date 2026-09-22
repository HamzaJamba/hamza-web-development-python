import json
from channels.generic.websocket import AsyncWebsocketConsumer


class VehicleTrackingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket at ws/tracking/<vehicle_id>/
    Manager dashboards connect here to get live GPS pushes for one truck.
    """

    async def connect(self):
        self.vehicle_id = self.scope["url_route"]["kwargs"]["vehicle_id"]
        self.group_name = f"vehicle_{self.vehicle_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def gps_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))


class FleetOverviewConsumer(AsyncWebsocketConsumer):
    """
    WebSocket at ws/tracking/fleet/
    Broadcasts every vehicle's GPS update — for the main live map dashboard.
    """

    async def connect(self):
        self.group_name = "fleet_overview"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def gps_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
