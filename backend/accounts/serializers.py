from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    work_email = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "full_name",
            "work_email",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        if attrs.get("work_email") and not attrs.get("email"):
            attrs["email"] = attrs["work_email"]
        if not attrs.get("email"):
            raise serializers.ValidationError({"email": "Email is required."})
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        validate_password(attrs["password"])
        if not attrs.get("username"):
            attrs["username"] = attrs["email"].split("@")[0]
            base = attrs["username"]
            counter = 1
            while User.objects.filter(username=attrs["username"]).exists():
                attrs["username"] = f"{base}{counter}"
                counter += 1
        if attrs.get("full_name") and not attrs.get("first_name"):
            parts = attrs["full_name"].strip().split(" ", 1)
            attrs["first_name"] = parts[0]
            attrs["last_name"] = parts[1] if len(parts) > 1 else ""
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm", None)
        validated_data.pop("full_name", None)
        validated_data.pop("work_email", None)
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class EmailLoginSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"] = serializers.EmailField(write_only=True)
        if "username" in self.fields:
            del self.fields["username"]

    def validate(self, attrs):
        from django.conf import settings

        email = attrs.pop("email", None)
        if email:
            try:
                user = User.objects.get(email__iexact=email)
                attrs[self.username_field] = getattr(user, self.username_field)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    {
                        "email": "No account with this email. Sign up first on this server.",
                        "error": "No account with this email. Sign up first on this server.",
                    }
                ) from None
        try:
            data = super().validate(attrs)
        except serializers.ValidationError as exc:
            detail = exc.detail
            if isinstance(detail, dict) and "error" not in detail:
                non_field = detail.get("non_field_errors") or detail.get("detail")
                if non_field:
                    msg = non_field[0] if isinstance(non_field, list) else str(non_field)
                    raise serializers.ValidationError(
                        {**detail, "error": "Invalid email or password."}
                    ) from exc
                raise serializers.ValidationError(
                    {**detail, "error": "Invalid email or password."}
                ) from exc
            raise
        profile, _ = UserProfile.objects.get_or_create(user=self.user)
        if settings.DEBUG and not profile.email_verified:
            profile.email_verified = True
            profile.save(update_fields=["email_verified"])
        if getattr(settings, "REQUIRE_EMAIL_VERIFICATION", False):
            if not profile.email_verified:
                raise serializers.ValidationError(
                    {
                        "email": "Verify your email before signing in.",
                        "error": "Verify your email before signing in.",
                    }
                )
        return data


class UserSerializer(serializers.ModelSerializer):
    email_verified = serializers.SerializerMethodField()
    plan = serializers.SerializerMethodField()
    generations_used = serializers.SerializerMethodField()
    generations_limit = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "email_verified",
            "plan",
            "generations_used",
            "generations_limit",
        )
        read_only_fields = fields

    def _profile(self, obj):
        return getattr(obj, "profile", None)

    def get_email_verified(self, obj):
        p = self._profile(obj)
        return bool(p and p.email_verified)

    def get_plan(self, obj):
        p = self._profile(obj)
        return p.plan if p else "free"

    def get_generations_used(self, obj):
        p = self._profile(obj)
        if p:
            p.reset_usage_if_needed()
            return p.generations_this_month
        return 0

    def get_generations_limit(self, obj):
        p = self._profile(obj)
        return p.generation_limit if p else 25


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        validate_password(attrs["password"])
        return attrs


class EmailVerifySerializer(serializers.Serializer):
    token = serializers.CharField()
