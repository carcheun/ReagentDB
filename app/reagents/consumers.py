import logging
import json
import redis
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

#redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, \
#    port=settings.REDIS_PORT, db=0)

class ReagentsConsumer(AsyncWebsocketConsumer):
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
    # on html side: display all connected stainers
    # on html side: display all connected stainer status
    # receive messages: like status
    # receive messages: uservisits page->request stainer status->return status
    # receive messages: stainer-connect->add to pool
    # user leaves-> send out that user has left

    async def connect(self):
        self.room_group_name = 'autostainer_clients'
        # join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

        if self.scope['query_string'] is not b'':
            query_str = self.scope['query_string'].decode('UTF-8')
            data = query_str.split('=')
            self.autostainer_sn = data[-1]
        else:
            self.autostainer_sn = 'webbrowser'
        logger.info('%s : %s connect', self.autostainer_sn, self.channel_name)
        #print(self.scope)
        # add user to my redis db
        #if self.autostainer_sn is not 'webbrowser':
        #    redis_instance.set('autostainer_' + self.autostainer_sn,"online")

    async def disconnect(self, close_code):
        # leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        #redis_instance.delete('autostainer_' + self.autostainer_sn)
        logger.info('%s : %s disconnect', self.autostainer_sn, self.channel_name)

    async def receive(self, text_data):
        logger.info(text_data)
        text_data_json = json.loads(text_data)
        
        if text_data_json.get('request', False):
            if text_data_json['request'] == 'request_stainer_status':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'get_stainer_status',
                        'request': 'get_stainer_status'
                    }
                )
        elif text_data_json.get('status', False):
            message = text_data_json['status']
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_message',
                    'message': message
                }
            )
        # client sends autostainer_sn here

        # send message to room group
        #await self.channel_layer.group_send(
        #    self.room_group_name,
        #    {
        #        'type': 'send_message',
        #        'message': message
        #    }
        #)

    async def get_stainer_status(self, event):
        message = event['request']
        # check how many are connected...
        #cnt = 0
        #for key in redis_instance.keys('autostainer_*'):
        #    cnt += 1
        await self.send(text_data=json.dumps({
            'request': message
        }))

    async def send_message(self, event):
        # send message to all clients in group
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))