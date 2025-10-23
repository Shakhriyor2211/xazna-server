from django.urls import path
from chat import consumers

chat_ws_urlpatterns = [
    path("message/<uuid:session_id>/", consumers.ChatConsumer.as_asgi(), name="chat_message_list")
]


