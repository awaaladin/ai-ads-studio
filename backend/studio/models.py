import uuid

from django.conf import settings
from django.db import models


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
    )
    business_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255, blank=True, default="")
    audience = models.CharField(max_length=512, blank=True, default="")
    tone = models.CharField(max_length=128, blank=True, default="")
    colors = models.CharField(max_length=32, blank=True, default="#8b5cf6")
    goal = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.business_name


class Asset(models.Model):
    FILE_IMAGE = "image"
    FILE_VIDEO = "video"
    FILE_PDF = "pdf"
    FILE_OTHER = "other"
    FILE_TYPE_CHOICES = [
        (FILE_IMAGE, "Image"),
        (FILE_VIDEO, "Video"),
        (FILE_PDF, "PDF"),
        (FILE_OTHER, "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="assets")
    file_type = models.CharField(max_length=16, choices=FILE_TYPE_CHOICES, default=FILE_OTHER)
    file = models.FileField(upload_to="assets/%Y/%m/", blank=True, null=True)
    file_url = models.URLField(max_length=1024, blank=True, default="")
    extracted_text = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class AdCreative(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="ad_creatives")
    copy = models.TextField()
    social_posts = models.JSONField(default=list)
    pdf_brochure_url = models.URLField(max_length=1024, blank=True, default="")
    pdf_file = models.FileField(upload_to="brochures/%Y/%m/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class AdBrief(models.Model):
    """Matches frontend2/create-ad.html form fields."""

    TONE_CHOICES = [
        ("friendly", "Friendly"),
        ("playful", "Playful"),
        ("stylish", "Stylish"),
        ("bold", "Bold"),
    ]
    PLATFORM_CHOICES = [
        ("meta", "Meta"),
        ("tiktok", "TikTok"),
        ("linkedin", "LinkedIn"),
        ("youtube", "YouTube"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ad_briefs",
    )
    product_service = models.CharField(max_length=512)
    audience = models.CharField(max_length=512)
    tone = models.CharField(max_length=32, choices=TONE_CHOICES, default="friendly")
    platform = models.CharField(max_length=32, default="meta")
    key_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product_service} ({self.platform})"


class AdVariant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brief = models.ForeignKey(AdBrief, on_delete=models.CASCADE, related_name="variants")
    headline = models.CharField(max_length=512)
    body = models.TextField()
    cta = models.CharField(max_length=255, blank=True, default="")
    platform = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class Campaign(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_ACTIVE = "active"
    STATUS_PAUSED = "paused"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_PAUSED, "Paused"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="campaigns",
    )
    name = models.CharField(max_length=255)
    platform = models.CharField(max_length=32, default="meta")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    brief = models.ForeignKey(
        AdBrief,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="campaigns",
    )
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    spend = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def ctr(self):
        if self.impressions == 0:
            return 0.0
        return round((self.clicks / self.impressions) * 100, 2)


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=64, db_index=True)
    resource_type = models.CharField(max_length=64, blank=True, default="")
    resource_id = models.CharField(max_length=64, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
