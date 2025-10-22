from django.urls import path
from chat.routing import chat_ws_urlpatterns
from channels.routing import URLRouter

ws_urlpatterns = [
    path("chat/", URLRouter(chat_ws_urlpatterns))
]