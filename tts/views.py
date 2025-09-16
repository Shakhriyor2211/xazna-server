from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from asgiref.sync import async_to_sync
from drf_yasg import openapi
from accounts.permissions import AuthPermission
from shared.models import AudioModel
from shared.views import CustomPagination
from tts.models import TTSModel
from tts.serializers import TTSSerializer, TTSListSerializer
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
            instance = serializer.save(audio=audio, user=request.user)

            tts = TTSListSerializer(instance)

            return Response(data=tts.data, status=status.HTTP_200_OK)

        except Exception as error:
            print(error)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class TTSListAPIView(APIView):
    permission_classes = [AuthPermission]

    @swagger_auto_schema(operation_description='TTS list...', manual_parameters=[
        openapi.Parameter(
            'page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'page_size', openapi.IN_QUERY, description="Items per page", type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'ordering', openapi.IN_QUERY, description="Comma-separated fields (e.g. `created_at,text`)",
            type=openapi.TYPE_STRING
        ),
    ])
    def get(self, request):
        ordering = request.query_params.get('ordering', '-created_at')


        queryset = TTSModel.objects.filter(user=request.user).order_by(ordering)

        paginator = CustomPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = TTSListSerializer(paginated_qs, many=True)

        return paginator.get_paginated_response(serializer.data)


class TTSSearchAPIView(APIView):
    permission_classes = [AuthPermission]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'q', openapi.IN_QUERY,
                description="Search by name",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
    )
    def get(self, request):
        q = request.GET['q'].strip()
        items = TTSModel.objects.filter(text__icontains=q, user=request.user).order_by('-created_at')
        serializer = TTSListSerializer(items, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class TTSDeleteAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'items': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="List of TTSModel IDs to delete"
                )
            },
        ),
    )
    def post(self, request):
        try:
            items = request.data.get('items')
            for item in items:
                TTSModel.objects.get(id=item).delete()

            return Response(data={'message': 'Items are successfully deleted.'}, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)