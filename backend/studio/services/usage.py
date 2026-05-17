from django.conf import settings
from rest_framework.exceptions import Throttled

from accounts.models import UserProfile


def get_or_create_profile(user) -> UserProfile:
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.reset_usage_if_needed()
    return profile


def check_generation_quota(user) -> UserProfile:
    if not user.is_authenticated:
        return None
    profile = get_or_create_profile(user)
    if profile.generations_this_month >= profile.generation_limit:
        raise Throttled(
            detail=(
                f"Monthly generation limit reached ({profile.generation_limit}). "
                "Upgrade plan or wait until next billing period."
            )
        )
    return profile


def record_generation(user, count: int = 1) -> None:
    if not user.is_authenticated:
        return
    profile = get_or_create_profile(user)
    profile.generations_this_month += count
    profile.save(update_fields=["generations_this_month"])
