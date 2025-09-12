from asgiref.sync import async_to_sync
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.permissions import AuthPermission
from shared.utils import send_post_request
from shared.views import CustomPagination
from stt.models import STTModel
from stt.serializers import AudioSerializer, STTListSerializer
from xazna import settings


class STTAPIView(APIView):
    permission_classes = [AuthPermission]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Speech to text...",
        request_body=AudioSerializer
    )
    def post(self, request):
        try:
            serializer = AudioSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            file = serializer.validated_data["file"]

            instance = serializer.save(user=request.user, name=file.name)

            res = async_to_sync(send_post_request)(file, settings.STT_SERVER, 'file')
            data = res.json()

            STTModel.objects.create(text=data["transcription"], user=request.user, audio=instance)

            return Response(data={'audio': instance.id, 'text': data["transcription"]}, status=status.HTTP_200_OK)

        except Exception as error:
            print(error)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class STTListAPIView(APIView):
    permission_classes = [AuthPermission]

    @swagger_auto_schema(operation_description='STT list...', manual_parameters=[
        openapi.Parameter(
            'page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'page_size', openapi.IN_QUERY, description="Items per page (max 100)", type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'ordering', openapi.IN_QUERY, description="Comma-separated fields (e.g. `created_at,text`)",
            type=openapi.TYPE_STRING
        ),
    ])
    def get(self, request):
        ordering = request.query_params.get('ordering', '-created_at')


        queryset = STTModel.objects.filter(user_id=request.user).order_by(ordering)

        paginator = CustomPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = STTListSerializer(paginated_qs, many=True)

        return paginator.get_paginated_response(serializer.data)


class STTDeleteAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'items': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="List of STTModel IDs to delete"
                )
            },
        ),
    )
    def post(self, request):
        try:
            items = request.data.get('items')
            for item in items:
                STTModel.objects.get(id=item).delete()

            return Response(data={'message': 'Items are successfully deleted.'}, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class STTSearchAPIView(APIView):
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
        items = STTModel.objects.filter(audio__name__icontains=q).order_by('-created_at')
        serializer = STTListSerializer(items, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)
