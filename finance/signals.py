from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import CustomUserModel
from finance.models import BalanceModel, SubscriptionModel, PlanModel


@receiver(post_save, sender=CustomUserModel)
def create_user_balance(sender, instance, created, **kwargs):
    if created:
        _, _ = PlanModel.objects.get_or_create(title="Enterprise")
        plan, _ = PlanModel.objects.get_or_create(title="Free")
        sub = SubscriptionModel.objects.create(user=instance, title=plan.title, credit=plan.monthly_credit, price=plan.monthly_price, discount=plan.monthly_discount, rate=plan.rate, rate_time=plan.rate_time)
        BalanceModel.objects.get_or_create(user=instance, subscription=sub)

