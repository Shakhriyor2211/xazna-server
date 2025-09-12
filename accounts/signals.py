from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUserModel, UserPictureModel


@receiver(post_save, sender=CustomUserModel)
def create_user_picture(sender, instance, created, **kwargs):
    if created and not hasattr(instance, "picture"):
        UserPictureModel.objects.create(user=instance)