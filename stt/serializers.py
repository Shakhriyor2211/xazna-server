from rest_framework import serializers

from shared.serializers import AudioSerializer
from stt.models import STTModel



class STTListSerializer(serializers.ModelSerializer):
    audio = AudioSerializer()
    class Meta:
        model = STTModel
        fields = ["id", "text", "audio", "created_at"]
        read_only_fields = ["id"]


class STTChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = STTModel
        fields = [
            "text",
        ]


