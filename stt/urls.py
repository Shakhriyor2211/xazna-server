from django.urls import path

from stt.views import STTAPIView, STTListAPIView, STTDeleteAPIView, STTSearchAPIView, STTChangeAPIView

urlpatterns = [
    path("generate/", STTAPIView.as_view(), name="stt_generate"),
    path("list/", STTListAPIView.as_view(), name="stt_list"),
    path("delete/", STTDeleteAPIView.as_view(), name="stt_delete"),
    path("change/<stt_id>/", STTChangeAPIView.as_view(), name="stt_change"),
    path("search/", STTSearchAPIView.as_view(), name="stt_search"),
]