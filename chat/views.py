import re

from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatSessionModel, ChatMessageModel
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from drf_yasg.utils import swagger_auto_schema

class ChatSessionListAPIView(APIView):
    auth_required = True

    def get(self, request):
        sessions = ChatSessionModel.objects.filter(user=request.user).order_by("-created_at")
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)

class ChatSessionDetailAPIView(APIView):
    auth_required = True

    def get(self, request, session_id):
        session = ChatSessionModel.objects.filter(id=session_id, user=request.user).first()
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)

class ChatMessageListAPIView(APIView):
    auth_required = True

    def get(self, request, session_id):
        session = ChatSessionModel.objects.filter(id=session_id, user=request.user).first()
        messages = session.messages.order_by("created_at")
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

class ChatSessionAPIView(APIView):
    auth_required = True

    @swagger_auto_schema(
        operation_description="Create a new chat session and first user message",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "message": openapi.Schema(type=openapi.TYPE_STRING, description="User message to start chat"),
            },
            required=["message"],
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "title": openapi.Schema(type=openapi.TYPE_STRING),
                    "created_at": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                    "updated_at": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                }
            ),
            400: "Bad Request",
        }
    )
    def post(self, request):
        try:
            message = request.data.get("message")

            if not message:
                return Response({"detail": "Message is required."}, status=status.HTTP_400_BAD_REQUEST)

            words = re.split(r"\s+|(?=[.,;?!])|(?<=[.,;])", message)

            title = ""

            for i, word in enumerate(words):
                if i > 0 and len(word) + len(title) > 20:
                    break

                if i > 0 and not word in [".", ",", ";", "?", "!"]:
                    title += " "

                title += word

            session = ChatSessionModel.objects.create(user=request.user, title=title, is_streaming=True)

            ChatMessageModel.objects.create(content=message, role="user", session=session)

            return Response(data={"slug": session.id}, status=status.HTTP_201_CREATED)


            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request, session_id):
        session = ChatSessionModel.objects.filter(id=session_id, user=request.user).first()
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
