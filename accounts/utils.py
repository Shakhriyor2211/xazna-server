import secrets
from datetime import timedelta
from django.utils import timezone

from xazna import settings


def generate_email_otp(old_code):
    new_code = "".join(secrets.choice("0123456789") for _ in range(6))
    while old_code == new_code:
        new_code = "".join(secrets.choice("0123456789") for _ in range(6))
    return new_code, timezone.now() + timedelta(minutes=settings.EMAIL_EXPIRE_TIME)


