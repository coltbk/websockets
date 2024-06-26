# import json

# from asgiref.sync import async_to_sync
# from channels.generic.websocket import WebsocketConsumer


# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = f"chat_{self.room_name}"

#         # Join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name, self.channel_name
#         )

#         self.accept()

#     def disconnect(self, close_code):
#         # Leave room group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name, self.channel_name
#         )

#     # Receive message from WebSocket
#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]

#         # Send message to room group
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name, {"type": "chat.message", "message": message}
#         )

#     # Receive message from room group
#     def chat_message(self, event):
#         message = event["message"]

#         # Send message to WebSocket
#         self.send(text_data=json.dumps({"message": message}))

##########################################################
# Asynchronus
##########################################################


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from channels.auth import login
from sensors.models import SensorReading
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer

@database_sync_to_async   
def get_latest_readings():
    #  return SensorReading.objects.latest("date")[:5]
        # must convert to list to get it to work
        return list(SensorReading.objects.all())[-1]

@receiver(post_save, sender=SensorReading)
def handle_new_readings(**kwargs):
    channel_layer = get_channel_layer()
    print(channel_layer)

    async_to_sync(channel_layer.group_send)(
        "chat",
        {"type": "chat.message", "message": json.dumps("receiver message")},
    )
    print('receiver')

    # print(kwargs.get('instance').param)
    # if kwargs.get('created', True):
    #     new_reading = get_latest_readings()
    #     print(f'new reading: {new_reading}')




class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # need to have authmiddleware etc. to get user
        # self.user = self.scope['user']
        # print(f'user: {self.user}')
        print(f'chat channel layer: {self.channel_layer}')
        print(f'chat channel name: {self.channel_name}')
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # self.room_group_name = f"chat_{self.room_name}"
        self.room_group_name = f"chat"
        print(f'room group name: {self.room_group_name}')

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        # await self.channel_layer.group_add('chat', self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # await self.channel_layer.group_discard('chat', self.channel_name)

    # Receive message from WebSocket, gets called once per message
    async def receive(self, text_data):
        # login the user to this session.
        # await login(self.scope, self.user)
        print(self.channel_layer)
        print(f'text_data: {text_data}')
        message=text_data
        # text_data_json = json.loads(text_data)
        # message = text_data_json["message"]
        print(f"from async receive: {message}")
        # print(f"from async receive: {self.scope['client']}")
        # print(f"from async receive: {self.scope['user']}")
        # print(self.scope)
        # print(self.group)
        # print(self.user)
        # print(self.username)


        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group, gets called once for each tab opne to the room
    async def chat_message(self, event):
        message = event["message"]
        print(f'in chat_message: {message}')


        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

class TestConsumer(AsyncWebsocketConsumer):
    channel_layer_alias = "test"

    async def connect(self):
        # self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # self.room_group_name = f"chat_{self.room_name}"

        # # Join test group
        print(f'test channel layer: {self.channel_layer}')
        # await self.channel_layer.group_add('test', self.channel_name)

        print("connection detected by TestConsumer")
        channel_layer = get_channel_layer()
        print(f"from TestConsumer: {channel_layer}")
        await self.accept()

        handle_new_readings()

    async def receive(self, text_data):
        # await login(self.scope, self.scope['user'])
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print(f"from TestConsumer: {message}")
        # print(f"from TestConsumer: {get_channel_layer}")
        # print(self.scope)
        print(f"from TestConsumer: {self.scope['client']}")
        # print(f"from TestConsumer: {self.scope['user']}")

        # database things
        # latest_readings = await self.get_latest_readings()
        # print(f'test_reading: {latest_readings}')

        send_message = "test_message"
        await self.send(text_data=json.dumps({"message": send_message}))

        # chatty = ChatConsumer()
        # await chatty.send(text_data=json.dumps({"message": send_message}))

    # async def disconnect(self, close_code):
        # Leave room group
        # await self.channel_layer.group_discard('test', self.channel_name)

        
    # async def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json["message"]
    #     print(f"from TestConsumer: {message}")
    #     print(f"from TestConsumer: {get_channel_layer}")


