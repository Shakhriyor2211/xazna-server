from django.urls import path
from chat.views import ChatSessionListAPIView, ChatSessionAPIView, ChatSessionItemAPIView, ChatMessageListAPIView

urlpatterns = [
    path("session/list/", ChatSessionListAPIView.as_view(), name="chat_session_list"),
    path("session/<uuid:session_id>/", ChatSessionItemAPIView.as_view(),  name="chat_session_item"),
    path("session/message/<uuid:session_id>/", ChatMessageListAPIView.as_view(),  name="chat_message_list"),
    path("session/generate/", ChatSessionAPIView.as_view(),  name="chat_session_generate")
]