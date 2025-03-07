import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from notifications.routing import websocket_urlpatterns
from channels.security.websocket import AllowedHostsOriginValidator
from notifications.consumers import NotificationConsumer
from notifications.middleware import TokenAuthMiddleware


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_inventory_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    )),
})