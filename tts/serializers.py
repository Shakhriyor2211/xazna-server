from rest_framework import serializers
from shared.serializers import AudioSerializer
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




class TTSListSerializer(serializers.ModelSerializer):
    audio = AudioSerializer()
    class Meta:
        model = TTSModel
        fields = ["id", "text", "audio", "created_at"]
        read_only_fields = ["id"]