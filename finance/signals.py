from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import CustomUserModel
from finance.models import BalanceModel


@receiver(post_save, sender=CustomUserModel)
def create_user_balance(sender, instance, created, **kwargs):
    if created and not hasattr(instance, "balance"):
        BalanceModel.objects.create(user=instance)