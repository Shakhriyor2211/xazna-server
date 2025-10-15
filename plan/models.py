from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from xazna.models import BaseModel, CreditRateBaseModel


class PlanModel(BaseModel):
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
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



class PlanMonthlyModel(BaseModel):
    plan = models.OneToOneField("PlanModel", on_delete=models.CASCADE, related_name="monthly")
    credit = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    price = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=1,
                                          validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)

class PlanAnnualModel(BaseModel):
    plan = models.OneToOneField("PlanModel", on_delete=models.CASCADE, related_name="annual")
    credit = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    price = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=1,
                                          validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)


class PlanRateModel(BaseModel):
    plan = models.OneToOneField("PlanModel", on_delete=models.CASCADE, related_name="rate")

    class Meta:
        db_table = "plan_rate"


class STTRateModel(BaseModel):
    rate = models.OneToOneField("PlanRateModel", on_delete=models.CASCADE, related_name="stt")
    class Meta:
        db_table = "plan_stt_rate"


class TTSRateModel(BaseModel):
    rate = models.OneToOneField("PlanRateModel", on_delete=models.CASCADE, related_name="tts")
    class Meta:
        db_table = "plan_tts_rate"


class ChatRateModel(BaseModel):
    rate = models.OneToOneField("PlanRateModel", on_delete=models.CASCADE, related_name="chat")
    max_sessions = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "plan_chat_rate"

class STTCreditRateModel(CreditRateBaseModel):
    stt = models.OneToOneField("STTRateModel", on_delete=models.CASCADE, related_name="credit")

    class Meta:
        db_table = "plan_stt_credit_rate"


class TTSCreditRateModel(CreditRateBaseModel):
    tts = models.OneToOneField("TTSRateModel", on_delete=models.CASCADE, related_name="credit")

    class Meta:
        db_table = "plan_tts_credit_rate"


class ChatCreditRateModel(CreditRateBaseModel):
    chat = models.OneToOneField("ChatRateModel", on_delete=models.CASCADE, related_name="credit")

    class Meta:
        db_table = "plan_chat_credit_rate"


class ChatSessionRateModel(BaseModel):
    chat = models.OneToOneField("ChatRateModel", on_delete=models.CASCADE, related_name="session")
    limit = models.PositiveBigIntegerField(default=0)
    usage = models.DecimalField(max_digits=16, decimal_places=4,
                                validators=[MinValueValidator(0)], default=0)

    class Meta:
        db_table = "plan_chat_session_rate"





