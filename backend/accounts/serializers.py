from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Maps signup.html: full name, work email, password."""

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
    """Maps signin.html: email + password."""

    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"] = serializers.EmailField(write_only=True)
        if "username" in self.fields:
            del self.fields["username"]

    def validate(self, attrs):
        email = attrs.pop("email", None)
        if email:
            try:
                user = User.objects.get(email__iexact=email)
                attrs[self.username_field] = getattr(user, self.username_field)
            except User.DoesNotExist:
                raise serializers.ValidationError({"email": "No account with this email."}) from None
        return super().validate(attrs)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "date_joined")
        read_only_fields = fields
