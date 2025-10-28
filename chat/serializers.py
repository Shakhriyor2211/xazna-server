from rest_framework import serializers
from .models import ChatSessionModel, ChatMessageModel



class ChatMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatMessageModel
        fields = ["id", "role", "content", "created_at", "updated_at"]
        extra_kwargs = {
            "role": {"read_only": True},
            "status": {"read_only": True}
        }




class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSessionModel
        fields = ["id", "title", "created_at", "updated_at"]
        extra_kwargs = {
            "title": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True}
        }
