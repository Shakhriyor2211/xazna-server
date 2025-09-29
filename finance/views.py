from decimal import Decimal
from drf_yasg import openapi
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from accounts.permissions import AuthPermission, AdminPermission
from finance.models import PlanModel, SubscriptionModel, BalanceModel
from finance.serializers import SubscriptionSerializer, SubscriptionListSerializer
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from shared.views import CustomPagination


class SubscriptionAPIView(APIView):
    permission_classes = [AuthPermission]

    @swagger_auto_schema(operation_description='Take subscription...', request_body=SubscriptionSerializer)
    def post(self, request):
        try:
            serializer = SubscriptionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            period = serializer.validated_data["period"]
            plan = PlanModel.objects.get(title=serializer.validated_data["plan"])
            balance = request.user.balance
            subscription = balance.subscription

            if period == "monthly":
                plan = {
                    "title": plan.title,
                    "price": plan.monthly_price,
                    "credit": plan.monthly_credit,
                    "discount": plan.monthly_discount,
                    "rate": plan.rate,
                    "rate_time": plan.rate_time,
                }
            else:
                plan = {
                    "title": plan.title,
                    "price": plan.annual_price,
                    "credit": plan.annual_credit,
                    "discount": plan.annual_discount,
                    "rate": plan.rate,
                    "rate_time": plan.rate_time,
                }

            if plan["title"] == "Enterprise" or plan["title"] == "Free" and period == "annual" or plan[
                "title"] == "Free" and subscription.title == "Free" and subscription.end_date > timezone.now():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            price = plan["price"] * (Decimal(100 - plan["discount"]) / Decimal(100))

            if plan["title"] != "Free" and price > balance.cash:
                return Response(data={"message": "Not enough funds, please top up your balance."},
                                status=status.HTTP_400_BAD_REQUEST)

            balance.subscription = SubscriptionModel.objects.create(user=request.user, period=period, **plan)
            balance.cash -= price

            if subscription.status == "active":
                subscription.status = "canceled"

            subscription.save()
            balance.save()

            return Response(data={"message": "Your plan changed successfully."}, status=status.HTTP_200_OK)

        except Exception as error:
            print(error)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubscriptionListAPIView(APIView):
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

        queryset = SubscriptionModel.objects.filter(user=request.user).order_by(ordering)

        paginator = CustomPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = SubscriptionListSerializer(paginated_qs, many=True)

        return paginator.get_paginated_response(serializer.data)


class SubscriptionCheckAPIView(APIView):
    permission_classes = [AuthPermission, AdminPermission]

    def get(self, request):
        subscriptions = SubscriptionModel.objects.filter(status="active", end_date__lt=timezone.now())

        for subscription in subscriptions:
            subscription.status = "expired"
            subscription.save()

            local_now = timezone.localtime(timezone.now())
            midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
            balance = BalanceModel.objects.get(user=subscription.user)
            plan = PlanModel.objects.get(title=subscription.title)

            if subscription.period == "monthly":
                plan = {
                    "title": plan.title,
                    "price": plan.monthly_price,
                    "credit": plan.monthly_credit,
                    "discount": plan.monthly_discount,
                    "rate": plan.rate,
                    "rate_time": plan.rate_time,
                }
            else:
                plan = {
                    "title": plan.title,
                    "price": plan.annual_price,
                    "credit": plan.annual_credit,
                    "discount": plan.annual_discount,
                    "rate": plan.rate,
                    "rate_time": plan.rate_time,
                }

            if subscription.auto_renew and subscription.title == "Free":
                balance.subscription = SubscriptionModel.objects.create(user=subscription.user, period=subscription.period,
                                                                        start_date=midnight, **plan)
                balance.save()


            elif subscription.auto_renew and balance.cash >= subscription.price:
                balance.cash -= subscription.price
                balance.subscription = SubscriptionModel.objects.create(user=subscription.user, period=subscription.period,
                                                                        start_date=midnight, **plan)
                balance.save()

        return Response(status=status.HTTP_200_OK)
