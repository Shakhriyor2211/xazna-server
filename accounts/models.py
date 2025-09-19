import mimetypes
import os, uuid , requests

from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from accounts.managers import CustomUserManager
from xazna.models import BaseModel
from xazna import settings


def generate_picture_name(_, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("users", filename)


class CustomUserModel(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email address", max_length=200, unique=True)
    first_name = models.CharField("first name", max_length=150)
    last_name = models.CharField("last name", max_length=150)
    role = models.CharField(choices=[('user', 'User'), ('admin', 'Admin')], default='user')
    is_active = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    regular_auth = models.BooleanField(default=False)
    google_auth = models.BooleanField(default=False)
    facebook_auth = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_password_update = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"

    objects = CustomUserManager()

    @property
    def is_staff(self):
        return self.role in ['admin', 'superadmin']

    @property
    def is_superuser(self):
        return self.role == 'superadmin'



    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = 'user'

    def __str__(self):
        return f'''{self.email}'''



class PictureModel(BaseModel):
    user=models.OneToOneField(CustomUserModel, on_delete=models.CASCADE, related_name="picture")
    portrait=models.ImageField(upload_to=generate_picture_name, blank=True, null=True)

    def portrait_url(self, url):
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            ext = mimetypes.guess_extension(content_type.split(";")[0]) or ".jpg"
            filename = f"{uuid.uuid4()}.{ext}"

            self.portrait.save(filename, ContentFile(response.content), save=True)

    class Meta:
        verbose_name = "Picture"
        verbose_name_plural = "Pictures"
        db_table = 'picture'


class EmailConfirmOtpModel(BaseModel):
    id = models.CharField(
        max_length=36,
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name="email_confirmations")
    code = models.CharField(max_length=6, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    remaining_attempts = models.SmallIntegerField(default=settings.EMAIL_MAX_ATTEMPTS)
    remaining_resends = models.SmallIntegerField(default=settings.EMAIL_MAX_RESENDS)
    task_id = models.CharField(max_length=255, null=True, blank=True)
    last_attempt = models.DateTimeField(default=timezone.now)
    last_resend = models.DateTimeField(default=timezone.now)
    status = models.CharField(choices=[('processing', 'Processing'), ('sent', 'Sent')], default='processing')

    class Meta:
        verbose_name = "Email confirmation otp"
        verbose_name_plural = "Email confirmation otps"
        db_table = 'email_otp'


class SocialAccountModel(BaseModel):
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name="social_account")
    provider = models.CharField(
        "provider",
        max_length=20,
        choices=[("google", "Google"), ("facebook", "Facebook"), ("apple", "Apple")]
    )
    provider_user_id = models.CharField("provider user ID", max_length=255, db_index=True)

    class Meta:
        unique_together = ("provider", "provider_user_id")
        verbose_name = "Social account"
        verbose_name_plural = "Social accounts"
        db_table = 'social_accounts'

    def __str__(self):
        return f'''{self.provider} account for {self.provider_user_id}'''


class PasswordResetTokenModel(BaseModel):
    slug = models.SlugField(unique=True, max_length=250, default=uuid.uuid4, null=True, blank=True)
    token = models.CharField(unique=True)
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='password_reset_token')
    task_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(choices=[('processing', 'Processing'), ('sent', 'Sent')], default='processing')

    class Meta:
        verbose_name = "Password reset token"
        verbose_name_plural = "Password reset tokens"
        db_table = 'password_reset_token'




