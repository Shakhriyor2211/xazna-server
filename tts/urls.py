from django.urls import path

from tts.views import TTSAPIView, TTSListAPIView, TTSSearchAPIView, TTSDeleteAPIView

urlpatterns = [
    path("generate/", TTSAPIView.as_view(), name="tts_generate"),
    path("list/", TTSListAPIView.as_view(), name="tts_list"),
    path("search/", TTSSearchAPIView.as_view(), name="tts_search"),
    path("delete/", TTSDeleteAPIView.as_view(), name="stt_delete"),
]