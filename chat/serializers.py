from rest_framework import serializers
from .models import ChatSessionModel, ChatMessageModel



class ChatMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatMessageModel
        fields = ["id", "role", "status", "content", "created_at", "updated_at"]
        extra_kwargs = {
            "role": {"read_only": True},
            "status": {"read_only": True}
        }


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSessionModel
        fields = ["id", "title", "first_content", "messages", "created_at", "updated_at"]
        extra_kwargs = {
            "title": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True}
        }
