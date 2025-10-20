from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from xazna.models import BaseModel, CreditPlanRateBaseModel


class PlanModel(BaseModel):
    title = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    chat_session = models.PositiveIntegerField(default=0)
    chat_context = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(
        "accounts.CustomUserModel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'''{self.id}'''

    class Meta:
        verbose_name = "Data"
        verbose_name_plural = "Data"
        ordering = ["pk"]
        db_table = "plan"



class PlanMonthlyModel(BaseModel):
    plan = models.OneToOneField("PlanModel", on_delete=models.CASCADE, related_name="monthly")
    credit = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    price = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=1,
                                          validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)
    class Meta:
        verbose_name = "Monthly fund"
        verbose_name_plural = "Monthly funds"
        db_table = "plan_monthly"

class PlanAnnualModel(BaseModel):
    plan = models.OneToOneField("PlanModel", on_delete=models.CASCADE, related_name="annual")
    credit = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    price = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    discount = models.DecimalField(max_digits=4, decimal_places=1,
                                          validators=[MinValueValidator(0), MaxValueValidator(100)], default=0)

    class Meta:
        verbose_name = "Annual fund"
        verbose_name_plural = "Annual funds"
        db_table = "plan_annual"


class PlanRateModel(BaseModel):
    plan = models.OneToOneField("PlanModel", on_delete=models.CASCADE, related_name="rate")

    class Meta:
        verbose_name = "Rate"
        verbose_name_plural = "Rates"
        db_table = "plan_rate"

    def __str__(self):
        return self.plan.title


class PlanSTTRateModel(BaseModel):
    rate = models.OneToOneField("PlanRateModel", on_delete=models.CASCADE, related_name="stt")

    class Meta:
        verbose_name = "STT rate"
        verbose_name_plural = "STT rates"
        db_table = "plan_stt_rate"

    def __str__(self):
        return self.rate.plan.title


class PlanTTSRateModel(BaseModel):
    rate = models.OneToOneField("PlanRateModel", on_delete=models.CASCADE, related_name="tts")

    class Meta:
        verbose_name = "TTS rate"
        verbose_name_plural = "TTS rates"
        db_table = "plan_tts_rate"

    def __str__(self):
        return self.rate.plan.title

class PlanChatRateModel(BaseModel):
    rate = models.OneToOneField("PlanRateModel", on_delete=models.CASCADE, related_name="chat")

    class Meta:
        verbose_name = "Chat rate"
        verbose_name_plural = "Chat rates"
        db_table = "plan_chat_rate"

    def __str__(self):
        return self.rate.plan.title

class PlanSTTCreditRateModel(CreditPlanRateBaseModel):
    stt = models.OneToOneField("PlanSTTRateModel", on_delete=models.CASCADE, related_name="credit")

    class Meta:
        verbose_name = "STT credit rate"
        verbose_name_plural = "STT credit rates"
        db_table = "plan_stt_credit_rate"


class PlanTTSCreditRateModel(CreditPlanRateBaseModel):
    tts = models.OneToOneField("PlanTTSRateModel", on_delete=models.CASCADE, related_name="credit")

    class Meta:
        verbose_name = "TTS credit rate"
        verbose_name_plural = "TTS credit rates"
        db_table = "plan_tts_credit_rate"


class PlanChatCreditRateModel(CreditPlanRateBaseModel):
    chat = models.OneToOneField("PlanChatRateModel", on_delete=models.CASCADE, related_name="credit")

    class Meta:
        verbose_name = "Chat credit rate"
        verbose_name_plural = "Chat credit rates"
        db_table = "plan_chat_credit_rate"



class PlanChatSessionRateModel(BaseModel):
    chat = models.OneToOneField("PlanChatRateModel", on_delete=models.CASCADE, related_name="session")
    limit = models.DecimalField(max_digits=16, decimal_places=4,
                                validators=[MinValueValidator(0)], default=0)

    class Meta:
        verbose_name = "Chat session rate"
        verbose_name_plural = "Chat session rates"
        db_table = "plan_chat_session_rate"





