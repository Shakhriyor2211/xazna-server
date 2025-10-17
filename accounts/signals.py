from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUserModel, PictureModel
from finance.models import BalanceModel
from plan.models import PlanModel
from subscription.models import SubscriptionModel, SubRateModel, SubSTTRateModel, SubTTSRateModel, SubChatRateModel, \
    SubSTTCreditRateModel, SubTTSCreditRateModel, SubChatCreditRateModel, SubChatSessionRateModel


@receiver(post_save, sender=CustomUserModel)
def create_user(sender, instance, created, **kwargs):
    if created:
        balance = BalanceModel.objects.create(user=instance)

        if not hasattr(instance, "picture"):
            PictureModel.objects.create(user=instance)

        plan = PlanModel.objects.filter(title="Free").first()

        if plan is not None:
            sub = SubscriptionModel.objects.create(user=instance, title=plan.title, credit=plan.monthly.credit,
                                                   price=plan.monthly.price, discount=plan.monthly.discount)
            sub.create_relations(plan)

            balance.subscription = sub
            balance.save()

