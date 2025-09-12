from rest_framework import serializers

from tts.models import TTSModel


class TTSSerializer(serializers.ModelSerializer):
    emotion = serializers.ChoiceField(
        choices=[("Neural", "Neural"), ("Happy", "Happy")],
        default="Happy"
    )


    class Meta:
        model = TTSModel
        fields = ["text", "audio", "model", "format", "emotion"]
        extra_kwargs = {
            "audio": {"read_only": True},
        }

