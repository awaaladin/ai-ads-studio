import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.utils import DatabaseError
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.models import EmailVerificationToken, PasswordResetToken, UserProfile
from accounts.services.email import send_password_reset_email, send_verification_email
from studio.services.audit import audit

from .serializers import (
    EmailLoginSerializer,
    EmailVerifySerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)


class AuthBurstThrottle(ScopedRateThrottle):
    scope = "auth_burst"


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle, AuthBurstThrottle]
    throttle_scope = "auth_burst"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                self.perform_create(serializer)
        except IntegrityError:
            return Response(
                {"email": ["An account with this email already exists."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DatabaseError as exc:
            logger.exception("register database error")
            detail = (
                str(exc)
                if settings.DEBUG
                else "Database is not ready. Run migrations on your production database (see docs/PRODUCTION.md)."
            )
            return Response(
                {"error": detail, "detail": detail},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as exc:
            logger.exception("register failed")
            detail = str(exc) if settings.DEBUG else "Registration failed. Check server logs."
            return Response(
                {
                    "error": detail,
                    "detail": detail,
                    "error_type": exc.__class__.__name__,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = serializer.save()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if settings.DEBUG or not getattr(settings, "REQUIRE_EMAIL_VERIFICATION", False):
            profile.email_verified = True
            profile.save(update_fields=["email_verified"])
        else:
            token = EmailVerificationToken.create_for_user(user)
            send_verification_email(user, token.token)
        audit(user, "user.register", "user", user.pk)


class LoginView(TokenObtainPairView):
    serializer_class = EmailLoginSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle, AuthBurstThrottle]
    throttle_scope = "auth_burst"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            email = request.data.get("email")
            if email:
                try:
                    user = User.objects.get(email__iexact=email)
                    audit(user, "user.login", "user", user.pk)
                except User.DoesNotExist:
                    pass
        return response


class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        audit(request.user, "user.logout", "user", request.user.pk)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        UserProfile.objects.get_or_create(user=user)
        return user


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle, AuthBurstThrottle]
    throttle_scope = "auth_burst"

    def post(self, request):
        ser = PasswordResetRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"].lower()
        try:
            user = User.objects.get(email__iexact=email)
            token = PasswordResetToken.create_for_user(user)
            send_password_reset_email(user, token.token)
            audit(user, "auth.password_reset_request", "user", user.pk)
        except User.DoesNotExist:
            pass
        return Response(
            {"detail": "If that email exists, a reset link was sent."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle, AuthBurstThrottle]
    throttle_scope = "auth_burst"

    def post(self, request):
        ser = PasswordResetConfirmSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            row = PasswordResetToken.objects.select_related("user").get(
                token=ser.validated_data["token"]
            )
        except PasswordResetToken.DoesNotExist:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        if not row.is_valid:
            return Response({"detail": "Token expired or used."}, status=status.HTTP_400_BAD_REQUEST)
        user = row.user
        user.set_password(ser.validated_data["password"])
        user.save()
        row.used_at = timezone.now()
        row.save(update_fields=["used_at"])
        audit(user, "auth.password_reset_confirm", "user", user.pk)
        return Response({"detail": "Password updated."}, status=status.HTTP_200_OK)


class EmailVerifyView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        ser = EmailVerifySerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            row = EmailVerificationToken.objects.select_related("user").get(
                token=ser.validated_data["token"]
            )
        except EmailVerificationToken.DoesNotExist:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        if not row.is_valid:
            return Response({"detail": "Token expired or used."}, status=status.HTTP_400_BAD_REQUEST)
        profile = row.user.profile
        profile.email_verified = True
        profile.save(update_fields=["email_verified"])
        row.used_at = timezone.now()
        row.save(update_fields=["used_at"])
        audit(row.user, "auth.email_verified", "user", row.user.pk)
        return Response({"detail": "Email verified."}, status=status.HTTP_200_OK)
