from django.urls import path
from chat import consumers

chat_ws_urlpatterns = [
    path("<uuid:session_id>/message/", consumers.ChatConsumer.as_asgi(), name="chat_message_list")
]


