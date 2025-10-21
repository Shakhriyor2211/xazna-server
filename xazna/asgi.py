import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from xazna.middleware import WSAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xazna.settings')
django_asgi_app = get_asgi_application()

from xazna.routing import ws_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": WSAuthMiddleware(URLRouter(ws_urlpatterns))
})
