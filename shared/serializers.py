from shared.models import AudioModel
from rest_framework import serializers

class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioModel
        fields = ["id", "name", "file"]
        read_only_fields = ["id", "name"]
        extra_kwargs = {
            "file": {"write_only": True}
        }

