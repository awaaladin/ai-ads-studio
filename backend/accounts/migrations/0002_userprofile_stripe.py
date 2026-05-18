from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_user_profile_tokens"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="stripe_customer_id",
            field=models.CharField(blank=True, db_index=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="stripe_subscription_id",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
