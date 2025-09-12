import uuid
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
