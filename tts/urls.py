from django.urls import path

from tts.views import TTSAPIView

urlpatterns = [
    path("generate/", TTSAPIView.as_view(), name="tts")
]