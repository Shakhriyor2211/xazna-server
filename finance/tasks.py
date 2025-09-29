from celery import shared_task
from django.utils import timezone

from finance.models import SubscriptionModel, BalanceModel, PlanModel


@shared_task
def check_subscriptions():
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




