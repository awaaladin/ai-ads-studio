# Generated migration for GenerationRecord

import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("studio", "0003_auditlog"),
    ]

    operations = [
        migrations.CreateModel(
            name="GenerationRecord",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "source_type",
                    models.CharField(
                        choices=[("ad_brief", "Ad brief"), ("project", "Project")],
                        max_length=32,
                    ),
                ),
                ("source_id", models.UUIDField()),
                ("input_data", models.JSONField(default=dict)),
                ("output_data", models.JSONField(default=dict)),
                ("variant_count", models.PositiveSmallIntegerField(default=0)),
                (
                    "status",
                    models.CharField(
                        choices=[("success", "Success"), ("failure", "Failure")],
                        default="success",
                        max_length=16,
                    ),
                ),
                ("error_message", models.CharField(blank=True, default="", max_length=512)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="generation_records",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="generationrecord",
            index=models.Index(fields=["user", "-created_at"], name="studio_gen_user_created_idx"),
        ),
        migrations.AddIndex(
            model_name="generationrecord",
            index=models.Index(fields=["source_type", "source_id"], name="studio_gen_source_idx"),
        ),
    ]
