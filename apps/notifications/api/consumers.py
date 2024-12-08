import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("test_group", self.channel_name)
        await self.accept()
        print("WebSocket connection opened!")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("test_group", self.channel_name)
        print("WebSocket connection closed!")

    async def test_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))
        print(f"Message received: {event['message']}")

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.group_name = f"user_{self.scope['user'].id}_notifications"
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
            print(f"Notification WebSocket connection opened - User: {self.scope['user'].username}")
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        print("Notification WebSocket connection closed")

    async def notification_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))
        print(f"Bildirim gönderildi: {event['message']}")