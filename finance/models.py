from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from xazna.models import BaseModel


class BalanceModel(BaseModel):
    user = models.OneToOneField("accounts.CustomUserModel", on_delete=models.CASCADE, related_name="balance")
    cash = models.DecimalField(max_digits=16, decimal_places=4, default=0)
    chargeable = models.BooleanField(default=True)
    subscription = models.OneToOneField("SubscriptionModel", on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name="subscription")

    def __str__(self):
        return f'''{self.id}'''

    class Meta:
        verbose_name = "Balance"
        verbose_name_plural = "Balances"
        db_table = "balance"


class SubscriptionModel(BaseModel):
    title = models.CharField(max_length=50)
    credit = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    expense = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    discount = models.DecimalField(max_digits=3, decimal_places=1,
                                   validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    auto_renew = models.BooleanField(default=True)
    rate = models.PositiveBigIntegerField(default=0)
    rate_time = models.PositiveIntegerField(default=0)
    rate_usage = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    rate_reset = models.DateTimeField(null=True, blank=True)
    price = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    status = models.CharField(
        choices=[("active", "active"), ("expired", "expired"), ("canceled", "canceled")],
        default="active")
    period = models.CharField(choices=[("monthly", "monthly"), ("annual", "annual")], default="monthly")
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey("accounts.CustomUserModel", on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        if not self.end_date:
            local_now = timezone.localtime(timezone.now())
            midnight = local_now.replace(hour=23, minute=59, second=59, microsecond=59)

            if self.period == "annual":
                self.end_date = midnight + relativedelta(years=1)
            else:
                self.end_date = midnight + relativedelta(months=1)

        super().save(*args, **kwargs)

    def __str__(self):
        return f'''{self.title}'''

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
        db_table = "subscription"


class PlanModel(BaseModel):
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    rate = models.PositiveBigIntegerField(default=0)
    rate_time = models.PositiveIntegerField(default=0)
    monthly_credit = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    monthly_price = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    annual_credit = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    annual_price = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    monthly_discount = models.DecimalField(max_digits=4, decimal_places=1,
                                           validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    annual_discount = models.DecimalField(max_digits=4, decimal_places=1,
                                          validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    user = models.ForeignKey(
        "accounts.CustomUserModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'''{self.title}'''

    class Meta:
        verbose_name = "Plans"
        verbose_name_plural = "Plans"
        ordering = ["pk"]
        db_table = "plan"
