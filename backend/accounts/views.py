from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.models import EmailVerificationToken, PasswordResetToken
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


class AuthBurstThrottle(ScopedRateThrottle):
    scope = "auth_burst"


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle, AuthBurstThrottle]
    throttle_scope = "auth_burst"

    def perform_create(self, serializer):
        user = serializer.save()
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
        return self.request.user


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
