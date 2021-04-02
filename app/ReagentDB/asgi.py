"""
ASGI config for ReagentDB project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""
"""
import os
import django
#from django.core.asgi import get_asgi_application
#from channels.routing import ProtocolTypeRouter, URLRouter
#from channels.auth import AuthMiddlewareStack
from channels.routing import get_default_application
from django.core.asgi import get_asgi_application


#import reagents.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReagentDB.settings')
django.setup()
application = get_asgi_application()
"""
#application = ProtocolTypeRouter({
#    "http": get_asgi_application(),
#    "websocket": AuthMiddlewareStack(
#        URLRouter(
#            reagents.routing.websocket_urlpatterns
#        )
#    ),
#})

import os

from django.conf import settings
from django.conf.urls import url
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ReagentDB.settings")

#settings.configure(
#    DEBUG=(os.environ.get("DEBUG", "") == "1"),
    # Disable host header validation
#    ALLOWED_HOSTS=["*"],
    # Make this module the urlconf
#    ROOT_URLCONF=__name__,
#)

django_asgi_app = get_asgi_application()

#from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from reagents.consumers import ReagentsConsumer



application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    #"http": django_asgi_app,

    # WebSocket chat handler
    #"websocket": AuthMiddlewareStack(
    #    URLRouter([
    #        url(r"^chat/$", ReagentsConsumer.as_asgi()),
    #    ])
    "websocket": URLRouter([url(r'ws/reagents/', ReagentsConsumer.as_asgi())])
})