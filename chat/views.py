from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from xazna.permissions import AuthPermission
from .models import ChatSessionModel, ChatMessageModel
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ChatSessionListAPIView(APIView):
    permission_classes = [AuthPermission]

    def get(self, request):
        sessions = ChatSessionModel.objects.filter(user=request.user)
        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create chat session",
        operation_description="Create a new chat session for the authenticated user.",
        request_body=ChatSessionSerializer,
        responses={201: ChatSessionSerializer, 400: "Bad Request"},
    )
    def post(self, request):
        try:
            serializer = ChatSessionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        except Exception as e:

            print(e)

            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ChatSessionDetailAPIView(APIView):
    permission_classes = [AuthPermission]

    def get(self, request, session_id):
        session = ChatSessionModel.objects.filter(id=session_id, user=request.user).first()
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)


    def delete(self, request, session_id):
        session = ChatSessionModel.objects.filter(id=session_id, user=request.user).first()
        if not session:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChatMessageListAPIView(APIView):
    permission_classes = [AuthPermission]

    def get(self, request, session_id):
        messages = ChatMessageModel.objects.filter(session__id=session_id, session__user=request.user)
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create chat message",
        request_body=ChatMessageSerializer,
        manual_parameters=[
            openapi.Parameter("session_id", openapi.IN_PATH, description="Chat session ID", type=openapi.TYPE_STRING)
        ],
    )
    def post(self, request, session_id):
        try:
            user_content = request.data.get("content")
            if not user_content:
                return Response({"content": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

            user_serializer = ChatMessageSerializer(data={
                "content": user_content
            })

            if not user_serializer.is_valid():
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            user_message = user_serializer.save(role="user", status="pending", session_id=session_id)

            assistant_content = f"Assistant reply to: {user_content}"
            assistant_serializer = ChatMessageSerializer(data={
                "content": assistant_content
            })
            if not assistant_serializer.is_valid():
                return Response(assistant_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            assistant_message = assistant_serializer.save(role="assistant", status="pending", session_id=session_id)


            return Response({
                "user": ChatMessageSerializer(user_message).data,
                "assistant": ChatMessageSerializer(assistant_message).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)



