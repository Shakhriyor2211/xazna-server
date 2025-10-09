from decimal import Decimal
from drf_yasg import openapi
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from accounts.permissions import AuthPermission, AdminPermission
from finance.models import PlanModel, SubscriptionModel, BalanceModel, TransactionModel
from finance.serializers import SubscriptionChangeSerializer, SubscriptionListSerializer, PlansSerializer, \
    SubscriptionManageSerializer, BalanceManageSerializer, TransactionSerializer
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from shared.views import CustomPagination
from django.db import transaction


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




class PlansAPIView(APIView):
    def get(self, request):
        serializer = PlansSerializer(PlanModel.objects.all(), many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


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

                balance.subscription = SubscriptionModel.objects.create(user=request.user, period=old_subscription.period,
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
                old_subscription = balance.subscription

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
                    "title"] == old_subscription.title and old_subscription.period == period:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

                price = plan["price"] * (Decimal(100 - plan["discount"]) / Decimal(100))

                if plan["title"] == "Free":
                    new_subscription = SubscriptionModel.objects.filter(title="Free", user=request.user).order_by(
                        "-start_date").first()
                    if new_subscription is not None and new_subscription.end_date >= timezone.now():
                        new_subscription.status = "active"
                        new_subscription.save()
                        balance.subscription = new_subscription
                    else:
                        balance.subscription = SubscriptionModel.objects.create(user=request.user, period=period, **plan)

                else:
                    if price > balance.cash:
                        return Response(data={"message": "Not enough funds, please top up your balance."},
                                        status=status.HTTP_400_BAD_REQUEST)

                    balance.subscription = SubscriptionModel.objects.create(user=request.user, period=period, **plan)
                    balance.cash -= price

                old_subscription.status = "canceled"
                old_subscription.save()
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



class TransactionListAPIView(APIView):
    permission_classes = [AuthPermission]

    def get(self, request):
        ordering = request.query_params.get('ordering', '-created_at')

        queryset = TransactionModel.objects.filter(user=request.user).order_by(ordering)

        paginator = CustomPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)

        serializer = TransactionSerializer(paginated_qs, many=True)

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
                    "price": current_plan.monthly_price,
                    "credit": current_plan.monthly_credit,
                    "discount": current_plan.monthly_discount,
                    "rate": current_plan.rate,
                    "rate_time": current_plan.rate_time,
                }

                if subscription.period == "annual":
                    plan = {
                        "title": current_plan.title,
                        "price": current_plan.annual_price,
                        "credit": current_plan.annual_credit,
                        "discount": current_plan.annual_discount,
                        "rate": current_plan.rate,
                        "rate_time": current_plan.rate_time,
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
                                                                            title="Free", price=free_plan.monthly_price,
                                                                            credit=free_plan.monthly_credit,
                                                                            discount=free_plan.monthly_discount,
                                                                            rate=free_plan.rate,
                                                                            rate_time=free_plan.rate_time,
                                                                            start_date=midnight)
                balance.save()

            return Response(status=status.HTTP_200_OK)
