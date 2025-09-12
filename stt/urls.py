from django.urls import path

from stt.views import STTAPIView, STTListAPIView, STTDeleteAPIView, STTSearchAPIView

urlpatterns = [
    path("generate/", STTAPIView.as_view(), name="stt_generate"),
    path("list/", STTListAPIView.as_view(), name="stt_list"),
    path("delete/", STTDeleteAPIView.as_view(), name="stt_delete"),
    path("search/", STTSearchAPIView.as_view(), name="stt_search"),
]