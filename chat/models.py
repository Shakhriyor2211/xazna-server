import uuid
from django.db import models
from xazna.models import BaseModel


class ChatSessionModel(BaseModel):
    id = models.CharField(
        max_length=36,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    user = models.ForeignKey("accounts.CustomUserModel", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    rate = models.PositiveBigIntegerField(default=0)
    rate_usage = models.PositiveBigIntegerField(default=0)

    class Meta:
        verbose_name = "Session"
        verbose_name_plural = "Sessions"
        db_table = "chat_session"

    def __str__(self):
        return self.title

class ChatMessageModel(BaseModel):
    id = models.CharField(
        max_length=36,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    session = models.ForeignKey("ChatSessionModel", on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=[("user", "user"), ("assistant", "assistant")])
    status = models.CharField(choices=[("pending", "pending"), ("completed", "completed"), ("failed", "failed")])
    content = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        db_table = "chat_message"