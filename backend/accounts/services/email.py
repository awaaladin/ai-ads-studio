import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_verification_email(user, token: str) -> None:
    base = getattr(settings, "PUBLIC_APP_URL", "http://127.0.0.1:8000").rstrip("/")
    link = f"{base}/verify-email.html?token={token}"
    subject = "Verify your AI Ads Studio email"
    body = (
        f"Hi {user.first_name or user.username},\n\n"
        f"Verify your email to use AI generation:\n{link}\n\n"
        f"Or POST to {base}/api/auth/verify-email/ with JSON {{\"token\": \"{token}\"}}\n\n"
        "This link expires in 48 hours."
    )
    _send(user.email, subject, body)


def send_password_reset_email(user, token: str) -> None:
    base = getattr(settings, "PUBLIC_APP_URL", "http://127.0.0.1:8000").rstrip("/")
    link = f"{base}/reset-password.html?token={token}"
    subject = "Reset your AI Ads Studio password"
    body = (
        f"Reset your password:\n{link}\n\n"
        f"Or POST to {base}/api/auth/password-reset/confirm/ with "
        f'{{"token": "{token}", "password": "...", "password_confirm": "..."}}\n\n'
        "Expires in 2 hours. Ignore if you did not request this."
    )
    _send(user.email, subject, body)


def _send(to_email: str, subject: str, body: str) -> None:
    if not to_email:
        return
    try:
        send_mail(
            subject,
            body,
            getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@aiads.studio"),
            [to_email],
            fail_silently=False,
        )
    except Exception:
        logger.info("Email (dev fallback) to=%s subject=%s\n%s", to_email, subject, body)
