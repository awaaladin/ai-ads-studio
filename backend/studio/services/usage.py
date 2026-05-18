from rest_framework.exceptions import Throttled

from accounts.models import UserProfile


class UsageLimitExceeded(Throttled):
    status_code = 429
    default_detail = "Usage limit reached. Upgrade required."
    default_code = "usage_limit_exceeded"


def get_or_create_profile(user) -> UserProfile:
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.reset_usage_if_needed()
    return profile


def check_generation_quota(user) -> UserProfile:
    if not user.is_authenticated:
        return None
    profile = get_or_create_profile(user)
    if profile.plan != UserProfile.PLAN_PRO and profile.generations_this_month >= profile.generation_limit:
        raise UsageLimitExceeded()
    return profile


def record_generation(user, count: int = 1) -> None:
    if not user.is_authenticated:
        return
    profile = get_or_create_profile(user)
    profile.generations_this_month += count
    profile.save(update_fields=["generations_this_month"])


def user_can_generate(user) -> bool:
    if not user or not user.is_authenticated:
        return True
    profile = get_or_create_profile(user)
    if profile.plan == UserProfile.PLAN_PRO:
        return True
    return profile.generations_this_month < profile.generation_limit
