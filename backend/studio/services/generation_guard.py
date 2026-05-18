"""Prevent duplicate rapid generation requests per user/resource."""

from django.conf import settings
from django.core.cache import cache


def _lock_key(user_id, resource_key: str) -> str:
    return f"gen_lock:{user_id}:{resource_key}"


def acquire_generation_lock(user_id, resource_key: str, ttl: int | None = None) -> bool:
    if not user_id:
        return True
    seconds = ttl or int(getattr(settings, "GENERATION_LOCK_SECONDS", 15))
    return cache.add(_lock_key(user_id, resource_key), "1", timeout=seconds)


def release_generation_lock(user_id, resource_key: str) -> None:
    if not user_id:
        return
    cache.delete(_lock_key(user_id, resource_key))
