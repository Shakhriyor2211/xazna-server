from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUserModel
from finance.models import BalanceModel
from plan.models import PlanModel
from subscription.models import SubscriptionModel


@receiver(post_save, sender=CustomUserModel)
def create_user_balance(sender, instance, created, **kwargs):
    if created:
        _, _ = PlanModel.objects.get_or_create(title="Enterprise")
        plan, _ = PlanModel.objects.get_or_create(title="Free")
        sub = SubscriptionModel.objects.create(user=instance, title=plan.title, credit=plan.monthly.credit, price=plan.monthly.price, discount=plan.monthly.discount, rate=plan.rate)
        BalanceModel.objects.get_or_create(user=instance, subscription=sub)

