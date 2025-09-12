from datetime import timedelta

from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from accounts.models import EmailConfirmOtpModel, PasswordResetTokenModel
from xazna import settings


@shared_task(name="tasks.send_email_confirmation")
def send_email_confirmation(email_id):
    email_otp = EmailConfirmOtpModel.objects.get(id=email_id)
    subject = "Confirmation Code"
    from_email = f"""no-reply <{settings.EMAIL_HOST_USER}>"""
    to = [email_otp.user.email]

    text_content = f"""Welcome to OCR. Your confirmation code is {email_otp.code}."""

    html_content = render_to_string("email/confirmation.html", {"code": email_otp.code})

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    email_otp.status = "sent"
    email_otp.save()



@shared_task(name="tasks.send_email_reset_password")
def send_email_reset_password(token_id, target):
    t = PasswordResetTokenModel.objects.get(id=token_id)
    subject = "Confirmation Code"
    from_email = f"""no-reply <{settings.EMAIL_HOST_USER}>"""
    to = [t.user.email]

    text_content = f"""Welcome to OCR. Your confirmation code is {t.slug}."""

    html_content = render_to_string("password/reset.html", {"target": f"""{target.rstrip("/")}/{t.slug}"""})

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    t.status = "sent"
    t.save()


@shared_task
def clean_password_reset_tokens():
    cutoff = timezone.now() - timedelta(minutes=settings.RESET_PASSWORD_EXPIRE_TIME)
    deleted_count, _ = PasswordResetTokenModel.objects.filter(created_at__lt=cutoff).delete()
    print(f"Deleted {deleted_count} expired tokens")