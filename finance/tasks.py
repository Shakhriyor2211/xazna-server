from celery import shared_task
from django.utils import timezone
from django.db import transaction

from finance.models import BalanceModel
from plan.models import PlanModel
from subscription.models import SubscriptionModel


@shared_task
def check_subscriptions():
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

