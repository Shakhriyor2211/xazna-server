from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from xazna.permissions import AuthPermission
from finance.models import TransactionModel, ExpenseModel
from finance.serializers import BalanceManageSerializer, TransactionSerializer, ExpenseListSerializer
from rest_framework import status
from rest_framework.response import Response
from shared.views import CustomPagination
from django.db import transaction


class ExpenseListAPIView(APIView):
    permission_classes = [AuthPermission]

    def get(self, request):
        ordering = request.query_params.get('ordering', '-created_at')

        queryset = ExpenseModel.objects.filter(user=request.user).order_by(ordering)

        paginator = CustomPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = ExpenseListSerializer(paginated_qs, many=True)

        return paginator.get_paginated_response(serializer.data)



class BalanceTopUpAPIView(APIView):
    permission_classes = [AuthPermission]

    @swagger_auto_schema(operation_description="Top up balance...", request_body=TransactionSerializer)
    def post(self, request):
        try:
            with transaction.atomic():
                serializer = TransactionSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(user=request.user)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
        except:
            return Response(data=serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BalanceManageAPIView(APIView):
    permission_classes = [AuthPermission]

    @swagger_auto_schema(operation_description='Manage subscription...', request_body=BalanceManageSerializer)
    def patch(self, request):
        try:
            serializer = BalanceManageSerializer(
                instance=request.user.balance,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionListAPIView(APIView):
    permission_classes = [AuthPermission]

    def get(self, request):
        ordering = request.query_params.get('ordering', '-created_at')

        queryset = TransactionModel.objects.filter(user=request.user).order_by(ordering)

        paginator = CustomPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = TransactionSerializer(paginated_qs, many=True)

        return paginator.get_paginated_response(serializer.data)

