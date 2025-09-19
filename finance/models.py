from django.core.validators import MinValueValidator
from django.db import models

from accounts.models import CustomUserModel
from xazna.models import BaseModel


class BalanceModel(BaseModel):
    user = models.OneToOneField(CustomUserModel, on_delete=models.CASCADE, related_name="balance")
    cash =  models.FloatField(default=0,)
    credits = models.FloatField(validators=[MinValueValidator(0)], default=0)

    class Meta:
        verbose_name = "Balance"
        verbose_name_plural = "Balance"
        db_table = 'balance'



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
