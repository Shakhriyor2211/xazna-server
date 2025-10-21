from datetime import timedelta
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from asgiref.sync import async_to_sync
from drf_yasg import openapi
from finance.models import ExpenseModel
from shared.models import AudioModel
from shared.views import CustomPagination
from tts.models import TTSModel, TTSModelModel, TTSEmotionModel, TTSAudioFormatModel
from tts.serializers import TTSSerializer, TTSListSerializer
from shared.utils import send_post_request, generate_audio
from xazna import settings
from django.db import transaction



class TTSSettingsAPIView(APIView):
    auth_required = True

    def get(self, request):
        models = list(TTSModelModel.objects.values_list("title", flat=True))
        emotions = list(TTSEmotionModel.objects.values_list("title", flat=True))
        audio_formats = list(TTSAudioFormatModel.objects.values_list("title", flat=True))

        return Response(data={
            "models": models,
            "emotions": emotions,
            "formats": audio_formats
        }, status=status.HTTP_200_OK)


class TTSAPIView(APIView):
    auth_required = True

    @swagger_auto_schema(
        operation_description="Text to speech...",
        request_body=TTSSerializer
    )
    def post(self, request):
        try:
            with transaction.atomic():
                serializer = TTSSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                data = serializer.validated_data

                plan = TTSModelModel.objects.get(title=data["model"])
                balance = request.user.balance
                subscription = balance.subscription
                credit_rate = subscription.rate.stt.credit

                if credit_rate.reset is None or credit_rate.reset < timezone.now():
                    credit_rate.reset = timezone.now() + timedelta(minutes=credit_rate.time)
                    credit_rate.usage = 0

                credit_avail = subscription.credit - subscription.credit_expense
                credit_active = min(credit_avail, credit_rate.limit - credit_rate.usage)
                char_length = len(data["text"])
                credit_usage = char_length * plan.credit
                cash_usage = 0


                if balance.chargeable and char_length > credit_active / plan.credit:
                    remainder = char_length - int(credit_active / plan.credit)
                    credit_usage = (char_length - remainder) * plan.credit
                    cash_usage = remainder * plan.cash

                    if cash_usage > balance.cash:
                        return Response(data={"message": "Not enough founds."},
                                            status=status.HTTP_403_FORBIDDEN)

                    balance.cash -= cash_usage

                else:
                    if char_length > credit_avail / plan.credit:
                        return Response(data={"message": "Not enough credits."},
                                        status=status.HTTP_403_FORBIDDEN)

                    if char_length > credit_active / plan.credit:
                        return Response(data={"message": "Request limit exceeded."},
                                        status=status.HTTP_403_FORBIDDEN)

                subscription.credit_expense += credit_usage
                credit_rate.usage += credit_usage

                res = async_to_sync(send_post_request)({"text": data["text"], "emotion": data.get("emotion")},
                                                       settings.TTS_SERVER)

                audio_instance = AudioModel.objects.create(user=request.user,
                                                           file=generate_audio(res.content, fmt=data["format"]))

                tts_instance = serializer.save(audio=audio_instance, user=request.user)

                ExpenseModel.objects.create(operation="tts", credit=credit_usage, cash=cash_usage, tts=tts_instance, user=request.user)

                tts = TTSListSerializer(tts_instance)

                balance.save()
                subscription.save()
                credit_rate.save()

                return Response(data=tts.data, status=status.HTTP_200_OK)


        except Exception as error:
            print(error)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TTSListAPIView(APIView):
    auth_required = True

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
    auth_required = True

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
    auth_required = True

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
                TTSModel.objects.get(id=item, user=request.user).delete()

            return Response(data={'message': 'Items are successfully deleted.'}, status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
