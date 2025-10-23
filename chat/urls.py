from django.urls import path
from chat.views import ChatSessionListAPIView, ChatSessionAPIView, ChatSessionDetailAPIView

urlpatterns = [
    path("session/list/", ChatSessionListAPIView.as_view(), name="chat_session_list"),
    path("session/<uuid:session_id>/", ChatSessionDetailAPIView.as_view(),  name="chat_session_detail"),
    path("session/generate/", ChatSessionAPIView.as_view(),  name="chat_session_generate")
]