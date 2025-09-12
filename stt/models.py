import uuid
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
        verbose_name = "STT"
        verbose_name_plural = "STT"
        db_table = 'stt'
