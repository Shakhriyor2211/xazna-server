import uuid
from django.core.validators import MinValueValidator
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
    first_content = models.TextField()
    is_streaming = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Session"
        verbose_name_plural = "Sessions"
        db_table = "chat_session"
        ordering = ["-created_at"]

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
    content = models.TextField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        db_table = "chat_message"



class ChatModelModel(BaseModel):
    title = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey("accounts.CustomUserModel", on_delete=models.CASCADE)
    credit = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)
    cash = models.DecimalField(max_digits=16, decimal_places=4, validators=[MinValueValidator(0)], default=0)

    class Meta:
        verbose_name = "Model"
        verbose_name_plural = "Models"
        db_table = 'chat_model'