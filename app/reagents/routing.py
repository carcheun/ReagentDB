#import os

#from channels.auth import AuthMiddlewareStack
#from channels.routing import ProtocolTypeRouter, URLRouter

#from django.urls import re_path, path
from django.conf.urls import url

from . import consumers

#websocket_urlpatterns = [
#    re_path(r'ws/reagents', \
#        consumers.ReagentsConsumer.as_asgi()),
#]

websocket_urlpatterns = [
    url(r'^websockets/reagents', consumers.ReagentsConsumer),
]

#application = ProtocolTypeRouter({
#    "websocket": AuthMiddlewareStack(
#        URLRouter(websocket_urlpatterns),
#    ),
#})
"""
        URLRouter(
            #reagents.routing.websocket_urlpatterns
            [
                path(r'ws/reagents/', consumers.ReagentsConsumer),
            ]
        )
"""