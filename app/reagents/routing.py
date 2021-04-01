import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from django.urls import re_path, path

from . import consumers

#websocket_urlpatterns = [
#    re_path(r'ws/reagents', \
#        consumers.ReagentsConsumer.as_asgi()),
#]

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            #reagents.routing.websocket_urlpatterns
            [
                path(r'ws/reagents', consumers.ReagentsConsumer),
            ]
        )
    ),
})