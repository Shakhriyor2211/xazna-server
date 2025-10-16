from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUserModel, PictureModel
from finance.models import BalanceModel


@receiver(post_save, sender=CustomUserModel)
def create_user(sender, instance, created, **kwargs):
    if created:
        if not hasattr(instance, "picture"):
            PictureModel.objects.create(user=instance)

        BalanceModel.objects.get_or_create(user=instance)
