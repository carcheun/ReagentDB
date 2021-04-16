"""
ASGI config for ReagentDB project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""
import os

from django.conf import settings
from django.conf.urls import url
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from reagents.consumers import ReagentsConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ReagentDB.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter([url(r'ws/reagents/', ReagentsConsumer.as_asgi())])
})