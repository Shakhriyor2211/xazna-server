from django.urls import path

from chat.views import ChatSessionListAPIView, ChatSessionDetailAPIView

urlpatterns = [
    path("session/", ChatSessionListAPIView.as_view(), name="chat_session_list"),
    path("session/<uuid:session_id>/", ChatSessionDetailAPIView.as_view(), name="chat_session_detail")
]