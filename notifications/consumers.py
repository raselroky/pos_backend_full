from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        #print(self.user)
        if self.user.is_authenticated:
            self.group_name = f'user_{self.user.id}' 
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
            #print(f"User connected: {self.user}")
        else:
            #print(f"User not authenticated: {self.user}")
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        #print(message)
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def notify(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
        print(f"Notification received in consumer for user {self.user.id}: {message}")



