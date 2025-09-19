import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from accounts.models import CustomUserModel
from xazna.models import BaseModel


class AudioModel(BaseModel):
    id = models.CharField(
        max_length=36,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    file = models.FileField(upload_to="audio/")
    name = models.CharField(default="document")

    class Meta:
        verbose_name = "Audio"
        verbose_name_plural = "Audios"
        db_table = 'audio'


class SubscriptionModel(BaseModel):
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    credits = models.FloatField(validators=[MinValueValidator(0)])
    monthly_cost = models.FloatField(validators=[MinValueValidator(0)])
    annual_cost =models.FloatField(validators=[MinValueValidator(0)])
    discount =models.FloatField(validators=[MinValueValidator(0)])
    user = models.ForeignKey(
        CustomUserModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscription",
    )

    class Meta:
        verbose_name = "Subscriptions"
        verbose_name_plural = "Subscriptions"
        db_table = 'subscription'
