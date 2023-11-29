import os
import chat.routing

import notification.routing
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.security.websocket import AllowedHostsOriginValidator  # new

from django.core.asgi import get_asgi_application

from config.tokenauth_middleware import (
    TokenAuthMiddleware
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(  # new
        TokenAuthMiddleware(URLRouter(chat.routing.websocket_urlpatterns))),
})

