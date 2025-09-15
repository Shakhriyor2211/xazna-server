from rest_framework import serializers

from shared.models import AudioModel
from stt.models import STTModel


class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioModel
        fields = ["file", "name"]
        read_only_fields = ["name"]



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


