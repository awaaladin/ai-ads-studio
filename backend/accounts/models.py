import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class UserProfile(models.Model):
    PLAN_FREE = "free"
    PLAN_PRO = "pro"
    PLAN_CHOICES = [
        (PLAN_FREE, "Free"),
        (PLAN_PRO, "Pro"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    email_verified = models.BooleanField(default=False)
    plan = models.CharField(max_length=16, choices=PLAN_CHOICES, default=PLAN_FREE)
    generations_this_month = models.PositiveIntegerField(default=0)
    billing_period_start = models.DateField(default=timezone.localdate)
    stripe_customer_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        indexes = [models.Index(fields=["plan"])]

    def reset_usage_if_needed(self):
        today = timezone.now().date()
        if today.month != self.billing_period_start.month or today.year != self.billing_period_start.year:
            self.generations_this_month = 0
            self.billing_period_start = today
            self.save(update_fields=["generations_this_month", "billing_period_start"])

    @property
    def generation_limit(self):
        if self.plan == self.PLAN_PRO:
            return int(getattr(settings, "GENERATION_LIMIT_PRO", 500))
        return int(getattr(settings, "GENERATION_LIMIT_FREE", 25))


class EmailVerificationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_tokens")
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def create_for_user(cls, user):
        token = secrets.token_urlsafe(32)
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(hours=48),
        )

    @property
    def is_valid(self):
        return self.used_at is None and timezone.now() < self.expires_at


class PasswordResetToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def create_for_user(cls, user):
        cls.objects.filter(user=user, used_at__isnull=True).update(used_at=timezone.now())
        token = secrets.token_urlsafe(32)
        return cls.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(hours=2),
        )

    @property
    def is_valid(self):
        return self.used_at is None and timezone.now() < self.expires_at
