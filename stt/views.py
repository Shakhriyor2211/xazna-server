import math
from datetime import timedelta

from asgiref.sync import async_to_sync
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.permissions import AuthPermission
from shared.models import AudioModel
from shared.utils import send_post_request, get_audio_duration
from shared.views import CustomPagination
from stt.models import STTModel, STTModelModel
from stt.serializers import STTListSerializer, STTChangeSerializer, STTSerializer
from xazna import settings
from django.utils import timezone
from django.db import transaction


class STTAPIView(APIView):
    permission_classes = [AuthPermission]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(operation_description='STT list...', request_body=STTSerializer)
    def post(self, request):
        try:
            with transaction.atomic():
                serializer = STTSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                model = serializer.validated_data["model"]

                file = serializer.validated_data["file"]

                plan = STTModelModel.objects.get(title=model)
                balance = request.user.balance
                subscription = balance.subscription

                if subscription.rate_reset is None or subscription.rate_reset < timezone.now():
                    subscription.rate_reset = timezone.now() + timedelta(minutes=subscription.rate_time)
                    subscription.rate_usage = 0

                credit_avail = subscription.credit - subscription.expense
                credit_active = min(credit_avail, subscription.rate - subscription.rate_usage)
                audio_duration = math.ceil(get_audio_duration(file))
                credit_usage = audio_duration * plan.credit
                cash_usage = 0

                if balance.chargeable and audio_duration > credit_active / plan.credit:
                    remainder = audio_duration - int(credit_active / plan.credit)
                    credit_usage = (audio_duration - remainder) * plan.credit
                    cash_usage = remainder * plan.cash

                    if cash_usage > balance.cash:
                        return Response(data={"message": "Not enough founds."},
                                        status=status.HTTP_403_FORBIDDEN)

                    balance.cash -= cash_usage

                else:
                    if audio_duration > credit_avail / plan.credit:
                        return Response(data={"message": "Not enough credits."},
                                        status=status.HTTP_403_FORBIDDEN)

                    if audio_duration > credit_active / plan.credit:
                        return Response(data={"message": "Request limit exceeded."},
                                        status=status.HTTP_403_FORBIDDEN)

                subscription.expense += credit_usage
                subscription.rate_usage += credit_usage

                res = async_to_sync(send_post_request)(file, settings.STT_SERVER, 'file')
                data = res.json()

                audio_instance = AudioModel.objects.create(user=request.user, file=file)
                stt_instance = STTModel.objects.create(text=data["transcription"], user=request.user, audio=audio_instance,
                                                       credit=credit_usage, cash=cash_usage)
                stt = STTListSerializer(stt_instance)

                balance.save()
                subscription.save()

                return Response(data=stt.data, status=status.HTTP_200_OK)


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

        queryset = STTModel.objects.filter(user=request.user).order_by(ordering)

        paginator = CustomPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = STTListSerializer(paginated_qs, many=True)

        return paginator.get_paginated_response(serializer.data)


class STTChangeAPIView(APIView):
    permission_classes = [AuthPermission]

    @swagger_auto_schema(
        operation_description="STT change...",
        request_body=STTChangeSerializer
    )
    def put(self, request, stt_id):
        stt_instance = STTModel.objects.get(id=stt_id, user=request.user)

        serializer = STTChangeSerializer(
            instance=stt_instance,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(data={"message": "Data successfully changed."}, status=status.HTTP_200_OK)


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
        items = STTModel.objects.filter(audio__name__icontains=q, user=request.user).order_by('-created_at')
        serializer = STTListSerializer(items, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)
