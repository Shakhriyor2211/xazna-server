import os
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
    name = models.CharField()

    def save(self, *args, **kwargs):
        ext = os.path.splitext(self.file.name)[1]
        if not self.name:
            self.name = self.file.name

        self.file.name = f"{uuid.uuid4()}{ext}"

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Audio"
        verbose_name_plural = "Audios"
        db_table = 'audio'


