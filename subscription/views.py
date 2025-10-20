from decimal import Decimal
from drf_yasg import openapi
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from xazna.permissions import AuthPermission, AdminPermission
from finance.models import BalanceModel
from plan.models import PlanModel
from subscription.models import SubscriptionModel
from subscription.serializers import SubscriptionChangeSerializer, SubscriptionListSerializer, \
    SubscriptionManageSerializer
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from shared.views import CustomPagination
from django.db import transaction


class SubscriptionRestartAPIView(APIView):
    permission_classes = [AuthPermission]

    @swagger_auto_schema(operation_description="Restart subscription...")
    def post(self, request):
        try:
            with transaction.atomic():
                balance = request.user.balance
                old_subscription = balance.subscription
                plan = PlanModel.objects.get(title=old_subscription.title)

                if old_subscription.period == "monthly":
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

                if plan["title"] == "Enterprise" or plan["title"] == "Free":
                    return Response(status=status.HTTP_400_BAD_REQUEST)

                price = plan["price"] * (Decimal(100 - plan["discount"]) / Decimal(100))

                if price > balance.cash:
                    return Response(data={"message": "Not enough funds, please top up your balance."},
                                    status=status.HTTP_400_BAD_REQUEST)

                balance.subscription = SubscriptionModel.objects.create(user=request.user,
                                                                        period=old_subscription.period,
                                                                        **plan)
                balance.cash -= price

                old_subscription.status = "canceled"

                old_subscription.save()
                balance.save()

                return Response(data={"message": "Subscription changed successfully."}, status=status.HTTP_200_OK)

        except Exception as error:
            print(error)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubscriptionChangeAPIView(APIView):
    permission_classes = [AuthPermission]

    @swagger_auto_schema(operation_description='Change subscription...', request_body=SubscriptionChangeSerializer)
    def post(self, request):
        try:
            with transaction.atomic():
                serializer = SubscriptionChangeSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                period = serializer.validated_data["period"]
                plan = PlanModel.objects.get(title=serializer.validated_data["plan"])

                balance = request.user.balance
                subscription = balance.subscription

                if plan.title == "Enterprise" or plan.title == "Free" and period == "annual" or plan.title == subscription.title and subscription.period == period:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

                if period == "monthly":
                    price = plan.monthly.price * (Decimal(100 - plan.monthly.discount) / Decimal(100))
                else:
                    price = plan.monthly.price * (Decimal(100 - plan.monthly.discount) / Decimal(100))

                if plan.title == "Free":
                    old_subscription = SubscriptionModel.objects.filter(title="Free", user=request.user).order_by(
                        "-start_date").first()
                    if old_subscription is not None and old_subscription.end_date >= timezone.now():
                        old_subscription.status = "active"
                        old_subscription.save()
                        balance.subscription = old_subscription
                    else:
                        sub = SubscriptionModel.objects.create(user=request.user, title=plan.title,
                                                                                credit=plan.monthly.credit,
                                                                                period=period, price=plan.monthly.price,
                                                                               discount=plan.monthly.discount)
                        sub.create_relations(plan)
                        balance.subscription = sub

                else:
                    if price > balance.cash:
                        return Response(data={"message": "Not enough funds, please top up your balance."},
                                        status=status.HTTP_400_BAD_REQUEST)

                    sub = SubscriptionModel.objects.create(user=request.user, title=plan.title,
                                                           credit=plan.monthly.credit,
                                                           period=period, price=price,
                                                           discount=plan.monthly.discount)

                    sub.create_relations(plan)
                    balance.subscription = sub
                    balance.cash -= price

                subscription.status = "canceled"
                subscription.save()
                balance.save()

                return Response(data={"message": "Subscription changed successfully."}, status=status.HTTP_200_OK)

        except Exception as error:
            print(error)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubscriptionManageAPIView(APIView):
    permission_classes = [AuthPermission]

    @swagger_auto_schema(operation_description='Manage subscription...', request_body=SubscriptionManageSerializer)
    def patch(self, request):
        try:
            serializer = SubscriptionManageSerializer(
                instance=request.user.balance.subscription,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except:
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
        with transaction.atomic():
            subscriptions = SubscriptionModel.objects.filter(status="active", end_date__lt=timezone.now())

            for subscription in subscriptions:
                subscription.status = "expired"
                subscription.save()

                local_now = timezone.localtime(timezone.now())
                midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
                balance = BalanceModel.objects.get(user=subscription.user)

                current_plan = PlanModel.objects.get(title=subscription.title)

                plan = {
                    "title": current_plan.title,
                    "price": current_plan.monthly.price,
                    "credit": current_plan.monthly.credit,
                    "discount": current_plan.monthly.discount,
                    "rate": current_plan.rate,
                }

                if subscription.period == "annual":
                    plan = {
                        "title": current_plan.title,
                        "price": current_plan.annual.price,
                        "credit": current_plan.annual.credit,
                        "discount": current_plan.annual.discount,
                        "rate": current_plan.rate,
                    }

                if subscription.auto_renew and balance.cash >= plan["price"]:
                    balance.cash -= subscription.price
                    balance.subscription = SubscriptionModel.objects.create(user=subscription.user,
                                                                            period=subscription.period,
                                                                            start_date=midnight, **plan)
                else:
                    free_plan = PlanModel.objects.get(title="Free")
                    balance.subscription = SubscriptionModel.objects.create(user=subscription.user,
                                                                            period="monthly",
                                                                            title="Free", price=free_plan.monthly.price,
                                                                            credit=free_plan.monthly.credit,
                                                                            discount=free_plan.monthly.discount,
                                                                            rate=free_plan.rate,
                                                                            start_date=midnight)
                balance.save()


            return Response(status=status.HTTP_200_OK)
