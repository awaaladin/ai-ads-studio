from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = "Set a user's plan (free or pro) for local testing without Stripe."

    def add_arguments(self, parser):
        parser.add_argument("email", type=str)
        parser.add_argument("plan", choices=["free", "pro"], type=str)

    def handle(self, *args, **options):
        user = User.objects.get(email__iexact=options["email"])
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.plan = options["plan"]
        profile.save(update_fields=["plan"])
        self.stdout.write(self.style.SUCCESS(f"{user.email} → {profile.plan}"))
