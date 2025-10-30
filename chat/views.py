from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from shared.utils import generate_title
from .models import ChatSessionModel, ChatMessageModel
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from drf_yasg.utils import swagger_auto_schema

class ChatSessionListAPIView(APIView):
    auth_required = True

    def get(self, request):
        sessions = ChatSessionModel.objects.filter(user=request.user).order_by("-created_at")
        serializer = ChatSessionSerializer(sessions, many=True)
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
                return Response({"message": "Message is required."}, status=status.HTTP_400_BAD_REQUEST)

            session = ChatSessionModel.objects.create(user=request.user, title=generate_title(message), is_streaming=True)

            ChatMessageModel.objects.create(content=message, role="user", session=session)

            return Response(data={"slug": session.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ChatSessionItemAPIView(APIView):
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

    def put(self, request, session_id):
        try:
            title = request.data.get("title")

            if title is None:
                return Response(data={"message": "Title is required."}, status=status.HTTP_400_BAD_REQUEST)

            session = ChatSessionModel.objects.filter(user=request.user, id=session_id).first()

            if session is None:
                return Response(data={"message": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

            session.title = generate_title(title)
            session.save()

            return Response(data={"title": session.title}, status=status.HTTP_200_OK)

        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)




    def delete(self, request, session_id):
        try:
            session = ChatSessionModel.objects.filter(user=request.user, id=session_id).first()

            if session is None:
                return Response(data={"message": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

            session.delete()

            return Response(data={"message": "Session successfully deleted."}, status=status.HTTP_200_OK)

        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
