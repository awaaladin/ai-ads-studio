"""Stripe Checkout + webhooks for Pro plan (optional until keys are configured)."""

import logging

from django.conf import settings

from accounts.models import UserProfile

logger = logging.getLogger("accounts.billing")


def stripe_configured() -> bool:
    return bool(getattr(settings, "STRIPE_SECRET_KEY", ""))


def _stripe():
    if not stripe_configured():
        raise RuntimeError("Stripe is not configured. Set STRIPE_SECRET_KEY and STRIPE_PRICE_ID_PRO.")
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def get_or_create_customer(user, profile: UserProfile) -> str:
    stripe = _stripe()
    if profile.stripe_customer_id:
        return profile.stripe_customer_id
    customer = stripe.Customer.create(
        email=user.email,
        metadata={"user_id": str(user.pk)},
    )
    profile.stripe_customer_id = customer.id
    profile.save(update_fields=["stripe_customer_id"])
    return customer.id


def create_checkout_session(user, profile: UserProfile) -> str:
    stripe = _stripe()
    customer_id = get_or_create_customer(user, profile)
    base = settings.PUBLIC_APP_URL.rstrip("/")
    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": settings.STRIPE_PRICE_ID_PRO, "quantity": 1}],
        success_url=settings.STRIPE_SUCCESS_URL or f"{base}/settings.html?billing=success",
        cancel_url=settings.STRIPE_CANCEL_URL or f"{base}/pricing.html?billing=cancelled",
        metadata={"user_id": str(user.pk)},
        subscription_data={"metadata": {"user_id": str(user.pk)}},
    )
    return session.url


def create_portal_session(profile: UserProfile) -> str:
    stripe = _stripe()
    if not profile.stripe_customer_id:
        raise RuntimeError("No billing account yet. Upgrade to Pro first.")
    base = settings.PUBLIC_APP_URL.rstrip("/")
    session = stripe.billing_portal.Session.create(
        customer=profile.stripe_customer_id,
        return_url=settings.STRIPE_PORTAL_RETURN_URL or f"{base}/settings.html",
    )
    return session.url


def set_plan_pro(profile: UserProfile, subscription_id: str = "") -> None:
    profile.plan = UserProfile.PLAN_PRO
    if subscription_id:
        profile.stripe_subscription_id = subscription_id
    profile.save(update_fields=["plan", "stripe_subscription_id"])


def set_plan_free(profile: UserProfile) -> None:
    profile.plan = UserProfile.PLAN_FREE
    profile.stripe_subscription_id = ""
    profile.save(update_fields=["plan", "stripe_subscription_id"])


def handle_webhook_event(payload: bytes, signature: str) -> None:
    stripe = _stripe()
    secret = settings.STRIPE_WEBHOOK_SECRET
    if not secret:
        raise RuntimeError("STRIPE_WEBHOOK_SECRET is not configured.")
    event = stripe.Webhook.construct_event(payload, signature, secret)
    event_type = event["type"]
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        _on_checkout_completed(data)
    elif event_type in ("customer.subscription.updated", "invoice.paid"):
        _on_subscription_active(data)
    elif event_type in ("customer.subscription.deleted",):
        _on_subscription_ended(data)


def _profile_for_metadata(meta: dict) -> UserProfile | None:
    user_id = (meta or {}).get("user_id")
    if not user_id:
        return None
    try:
        return UserProfile.objects.select_related("user").get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return None


def _on_checkout_completed(session: dict) -> None:
    profile = _profile_for_metadata(session.get("metadata") or {})
    if not profile:
        customer_id = session.get("customer")
        if customer_id:
            profile = UserProfile.objects.filter(stripe_customer_id=customer_id).first()
    if not profile:
        logger.warning("checkout.session.completed: no profile for session %s", session.get("id"))
        return
    sub_id = session.get("subscription") or ""
    set_plan_pro(profile, str(sub_id) if sub_id else "")
    logger.info("user %s upgraded to pro", profile.user_id)


def _on_subscription_active(subscription: dict) -> None:
    status = subscription.get("status", "")
    meta = subscription.get("metadata") or {}
    profile = _profile_for_metadata(meta)
    if not profile and subscription.get("customer"):
        profile = UserProfile.objects.filter(stripe_customer_id=subscription["customer"]).first()
    if not profile:
        return
    if status in ("active", "trialing"):
        set_plan_pro(profile, subscription.get("id", ""))
    elif status in ("canceled", "unpaid", "past_due", "incomplete_expired"):
        set_plan_free(profile)


def _on_subscription_ended(subscription: dict) -> None:
    customer_id = subscription.get("customer")
    profile = UserProfile.objects.filter(stripe_customer_id=customer_id).first()
    if profile:
        set_plan_free(profile)
        logger.info("user %s downgraded to free", profile.user_id)
