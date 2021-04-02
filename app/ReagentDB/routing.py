from channels.routing import ProtocolTypeRouter

from channels.routing import URLRouter
import reagents.routing

application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    'websocket': URLRouter(reagents.routing.websocket_urlpatterns),
})
