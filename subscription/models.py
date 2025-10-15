from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from xazna.models import BaseModel, CreditRateBaseModel


class SubscriptionModel(BaseModel):
    title = models.CharField(max_length=50)
    credit = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    expense = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    discount = models.DecimalField(max_digits=3, decimal_places=1,
                                   validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    auto_renew = models.BooleanField(default=False)
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
        db_table = "sub"



class SubscriptionRateModel(BaseModel):
    subscription = models.OneToOneField("SubscriptionModel", on_delete=models.CASCADE, related_name="rate")

    class Meta:
        db_table = "sub_rate"



class STTRateModel(BaseModel):
    rate = models.OneToOneField("SubscriptionRateModel", on_delete=models.CASCADE, related_name="stt")
    class Meta:
        db_table = "sub_stt_rate"


class TTSRateModel(BaseModel):
    rate = models.OneToOneField("SubscriptionRateModel", on_delete=models.CASCADE, related_name="tts")
    class Meta:
        db_table = "sub_tts_rate"


class ChatRateModel(BaseModel):
    rate = models.OneToOneField("SubscriptionRateModel", on_delete=models.CASCADE, related_name="chat")
    max_sessions = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "sub_chat_rate"

class STTCreditRateModel(CreditRateBaseModel):
    stt = models.OneToOneField("STTRateModel", on_delete=models.CASCADE, related_name="credit")

    class Meta:
        db_table = "sub_stt_credit_rate"


class TTSCreditRateModel(CreditRateBaseModel):
    tts = models.OneToOneField("TTSRateModel", on_delete=models.CASCADE, related_name="credit")

    class Meta:
        db_table = "sub_tts_credit_rate"


class ChatCreditRateModel(CreditRateBaseModel):
    chat = models.OneToOneField("ChatRateModel", on_delete=models.CASCADE, related_name="credit")

    class Meta:
        db_table = "sub_chat_credit_rate"


class ChatSessionRateModel(BaseModel):
    chat = models.OneToOneField("ChatRateModel", on_delete=models.CASCADE, related_name="session")
    limit = models.PositiveBigIntegerField(default=0)
    usage = models.DecimalField(max_digits=16, decimal_places=4,
                                validators=[MinValueValidator(0)], default=0)

    class Meta:
        db_table = "sub_chat_session_rate"


