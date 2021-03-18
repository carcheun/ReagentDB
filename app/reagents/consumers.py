import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ConnectionConsumer(AsyncWebsocketConsumer):
    # dont channel layer since the stainers do not need to talk to each other ?
    # dont really need to broadcast anything
    # ashome/autostainer should have a listener for a disconnect signal
    # TODO: user visits page, list number of online users
    # TODO: user visits page, list what stainer is doing what step
    # have to have channels and groups (TBD)
    # or
    # broadcast message to all users, users return IDLE, BLA, BLA, BLA, BLA
    # page displays information :)
    # SCENARIOS:
    # server disconnect, client trigger that connection closed, server has issue
    # visit 'homepage': webpage requests information on all stainers
    #       server recieves message, sends ping request
    #       client recieves ping, returns pong
    #       html page updates with information~

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        print("client connected")
        
        # join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    