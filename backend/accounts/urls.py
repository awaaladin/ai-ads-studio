from django.urls import path

from .billing_views import (
    BillingCheckoutView,
    BillingPortalView,
    BillingStatusView,
    StripeWebhookView,
)
from .views import (
    EmailVerifyView,
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RefreshView,
    RegisterView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="auth-password-reset"),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="auth-password-reset-confirm",
    ),
    path("verify-email/", EmailVerifyView.as_view(), name="auth-verify-email"),
    path("billing/status/", BillingStatusView.as_view(), name="billing-status"),
    path("billing/checkout/", BillingCheckoutView.as_view(), name="billing-checkout"),
    path("billing/portal/", BillingPortalView.as_view(), name="billing-portal"),
    path("billing/webhook/", StripeWebhookView.as_view(), name="billing-webhook"),
]
