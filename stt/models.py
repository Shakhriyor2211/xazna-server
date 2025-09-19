import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from accounts.models import CustomUserModel
from shared.models import AudioModel
from xazna.models import BaseModel


class STTModel(BaseModel):
    id = models.CharField(
        max_length=36,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    text = models.CharField(null=True, blank=True)
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    audio = models.OneToOneField(AudioModel, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Data"
        verbose_name_plural = "Data"
        db_table = 'stt_data'


class STTModelModel(BaseModel):
    title = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    credit = models.FloatField(validators=[MinValueValidator(0)])
    cash = models.FloatField(validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = "Models"
        verbose_name_plural = "Models"
        db_table = 'stt_model'


