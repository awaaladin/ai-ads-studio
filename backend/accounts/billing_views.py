from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserProfile
from accounts.services.stripe_billing import (
    create_checkout_session,
    create_portal_session,
    handle_webhook_event,
    stripe_configured,
)
from studio.services.usage import get_or_create_profile


class BillingStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = get_or_create_profile(request.user)
        return Response(
            {
                "plan": profile.plan,
                "generations_used": profile.generations_this_month,
                "generations_limit": profile.generation_limit,
                "stripe_enabled": stripe_configured(),
                "product": {
                    "name": "AI Ads Studio",
                    "tagline": "AI ad copy for marketers — briefs, variants, and export-ready copy.",
                },
                "pricing": {
                    "free": {
                        "generations_per_month": int(settings.GENERATION_LIMIT_FREE),
                        "price_usd": 0,
                    },
                    "pro": {
                        "generations_per_month": int(settings.GENERATION_LIMIT_PRO),
                        "price_usd": getattr(settings, "STRIPE_PRO_PRICE_USD", 29),
                    },
                },
            }
        )


class BillingCheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not stripe_configured():
            return Response(
                {
                    "error": "Billing is not configured on this server.",
                    "detail": "Set STRIPE_SECRET_KEY and STRIPE_PRICE_ID_PRO.",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        profile = get_or_create_profile(request.user)
        if profile.plan == UserProfile.PLAN_PRO:
            return Response(
                {"error": "You are already on Pro.", "detail": "You are already on Pro."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            url = create_checkout_session(request.user, profile)
        except Exception as exc:
            return Response(
                {"error": str(exc), "detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({"url": url})


class BillingPortalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not stripe_configured():
            return Response(
                {"error": "Billing is not configured.", "detail": "Billing is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        profile = get_or_create_profile(request.user)
        try:
            url = create_portal_session(profile)
        except Exception as exc:
            return Response(
                {"error": str(exc), "detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"url": url})


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        if not stripe_configured():
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        try:
            handle_webhook_event(request.body, signature)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"received": True})
