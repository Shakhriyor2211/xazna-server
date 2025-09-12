from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from asgiref.sync import async_to_sync

from accounts.permissions import AuthPermission
from shared.models import AudioModel
from tts.serializers import TTSSerializer
from shared.utils import send_post_request, generate_audio
from xazna import settings


class TTSAPIView(APIView):
    permission_classes = [AuthPermission]

    @swagger_auto_schema(
        operation_description="Text to speech...",
        request_body=TTSSerializer
    )
    def post(self, request):
        try:
            serializer = TTSSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            res = async_to_sync(send_post_request)({"emotion": data.get("emotion"), "text": data["text"]},
                                                   settings.TTS_SERVER)

            audio = AudioModel.objects.create(user=request.user, file=generate_audio(res.content, fmt=data["format"]))
            serializer.save(audio=audio, user=request.user)

            return Response(data={'audio': audio.id}, status=status.HTTP_200_OK)

        except Exception as error:
            print(error)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)



