from django.contrib.auth import authenticate
from django.core.validators import validate_email
from rest_framework import serializers
from accounts.exceptions import AuthException, PermissionException, ValidationException
from accounts.models import CustomUserModel, EmailConfirmOtpModel, PictureModel


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        try:
            validate_email(value)
        except serializers.ValidationError:
            raise AuthException(message="Enter a valid email address.", code="invalid_credentials")
        return value

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise AuthException(message="Email and password are required.", code="invalid_credentials")

        user = authenticate(username=email, password=password)

        if user is None:
            raise AuthException(message="Invalid credentials.", code="invalid_credentials")

        elif user.is_blocked:
            raise PermissionException(message="Account is blocked.", code="blocked_user")

        return {"user": user}


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUserModel
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
            "is_active",
            "is_blocked"
        ]

        extra_kwargs = {
            "password": {"write_only": True},
            "is_active": {"read_only": True},
            "is_blocked": {"read_only": True},
        }

    def validate_email(self, email):
        if CustomUserModel.objects.filter(email=email, regular_auth=True).exists():
            raise ValidationException(data={"email": "Email is already taken."})
        return email

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise ValidationException(data={"confirm_password": "Password and Confirm Password do not match."})
        return data

    def save(self, **kwargs):
        validated_data = self.validated_data.copy()
        validated_data.pop("confirm_password")

        user, created = CustomUserModel.objects.get_or_create(
            email=validated_data["email"],
            defaults={
                "first_name": validated_data["first_name"],
                "last_name": validated_data["last_name"],
                "regular_auth": True
            }
        )

        if not created:
            if not user.regular_auth:
                user.regular_auth = True
                user.save(update_fields=["regular_auth"])

        user.set_password(validated_data["password"])
        user.save(update_fields=["password"])

        return user






class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class VerifyTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class VerifyEmailCodeSerializer(serializers.ModelSerializer):
    otp_id = serializers.CharField()

    class Meta:
        model = EmailConfirmOtpModel
        fields = ["code", "otp_id"]


class ResendEmailCodeSerializer(serializers.Serializer):
    otp_id = serializers.CharField()


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
        # min_length=8,
        # max_length=128,
        style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        write_only=True,
        # min_length=8,
        # max_length=128,
        style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        # min_length=8,
        # max_length=128,
        style={"input_type": "password"}
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise ValidationException(data={"old_password": "Old password is incorrect."})
        return value

    def validate(self, attrs):
        if attrs["old_password"] == attrs["new_password"]:
            raise ValidationException(data={"new_password": "New password cannot be the same as the old password."})

        elif attrs["new_password"] != attrs["confirm_password"]:
            raise ValidationException(data={"confirm_password": "Passwords do not match."})

        return attrs




class ProfileChangeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUserModel
        fields = [
            "first_name",
            "last_name",
        ]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }


class PictureModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PictureModel
        fields = ["portrait"]


class UserSerializer(serializers.ModelSerializer):
    picture = PictureModelSerializer(read_only=True)

    class Meta:
        model = CustomUserModel
        fields = ["id", "first_name", "last_name", "email", "picture", "created_at", "last_password_update", "regular_auth", "is_active", "is_blocked"]



