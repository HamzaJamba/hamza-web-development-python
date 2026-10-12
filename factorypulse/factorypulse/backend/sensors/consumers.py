import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MachineConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.machine_id = self.scope["url_route"]["kwargs"]["machine_id"]
        self.group_name = f"machine_{self.machine_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def sensor_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))


class PlantOverviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "plant_overview"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def sensor_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
