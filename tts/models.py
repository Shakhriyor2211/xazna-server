from django.db import models
from accounts.models import CustomUserModel
from shared.models import AudioModel
from xazna.models import BaseModel


class TTSModel(BaseModel):
    text = models.CharField()
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    audio = models.OneToOneField(AudioModel, null=True, blank=True, on_delete=models.SET_NULL)
    emotion = models.CharField(choices=[('Neural', 'Neural'), ('Happy', 'Happy')], default='Happy')
    model = models.CharField(choices=[('iroda', 'iroda'), ('surayyo_v2', 'surayyo_v2')], default='surayyo_v2')
    format = models.CharField(
        choices=[('mp3', 'MP3'), ('wav', 'WAV'), ('ogg', 'OGG'), ('flac', 'FLAC'), ('aac', 'AAC')], default='mp3')

    class Meta:
        verbose_name = "TTS"
        verbose_name_plural = "TTS"
        db_table = 'tts'
