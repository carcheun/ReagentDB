"""
ASGI config for ReagentDB project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
#from channels.routing import ProtocolTypeRouter, URLRouter
#from channels.auth import AuthMiddlewareStack
from channels.routing import get_default_application
#import reagents.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReagentDB.settings')
django.setup()
application = get_default_application()

#application = ProtocolTypeRouter({
#    "http": get_asgi_application(),
#    "websocket": AuthMiddlewareStack(
#        URLRouter(
#            reagents.routing.websocket_urlpatterns
#        )
#    ),
#})