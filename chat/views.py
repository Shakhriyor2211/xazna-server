import re

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ChatSessionModel
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from drf_yasg.utils import swagger_auto_schema

class ChatSessionListAPIView(APIView):
    auth_required = True

    def get(self, request):
        sessions = ChatSessionModel.objects.filter(user=request.user)
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
        serializer = ChatMessageSerializer(session.messages, many=True)
        return Response(data={"contents": serializer.data, "first_content": session.first_content}, status=status.HTTP_200_OK)

class ChatSessionAPIView(APIView):
    auth_required = True

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
                first_content = serializer.validated_data.get("first_content")
                words = re.split(r"\s+|(?=[.,;?!])|(?<=[.,;])", first_content)

                title = ""

                for i, word in enumerate(words):
                    if i > 0 and len(word) + len(title) > 20:
                        break

                    if i > 0 and not word in [".", ",", ";", "?", "!"]:
                        title += " "

                    title += word


                serializer.save(user=request.user, title=title)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

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
