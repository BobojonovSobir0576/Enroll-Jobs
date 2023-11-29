""" Django Libary """
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from django.contrib import auth
from django.utils.encoding import (
    force_str,
    smart_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)
from django.contrib.auth.password_validation import validate_password
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import reverse

""" Django Rest Framework Libary """
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator


class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    groups = RolesSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "email", "groups"]


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=50, min_length=2)
    password = serializers.CharField(max_length=50, min_length=1)

    class Meta:
        model = User
        fields = ["username", "password"]
        read_only_fields = ("username",)

    def validate_username(self, value):
        if not value.strip():
            raise serializers.ValidationError("Username cannot be empty.")
        return value



class CreateAdminHrSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255, min_length=5, required=True,
                                     validators=[UniqueValidator(queryset=User.objects.all())])

    first_name = serializers.CharField(max_length=255, min_length=5, required=True)
    last_name = serializers.CharField(max_length=255, min_length=5, required=True)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "groups", "password"]

    def validate(self, attrs):
        username = attrs.get("username", "")

        if not username.isalnum():
            raise serializers.ValidationError(
                "The username should only contain alphanumeric characters"
            )
        return super().validate(attrs)

    def create(self, validated_data):

        groups = validated_data.pop('groups')
        create = User.objects.create_user(**validated_data)
        for i in groups:
            create.groups.add(i)
            create.save()
        return create


class UserDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", 'email']

        def update(self, instance, validated_data):
            instance.model_method()
            update = super().update(instance, validated_data)
            return update


class PasswordResetCompleteSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, max_length=32, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('Invalid link', 401)

            user.set_password(password)
            user.save()
            return user
        except Exception:
            raise AuthenticationFailed('Invalid link', 401)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email',]


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    default_error_message = {"bad_token": ("Token is expired or invalid")}

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail("bad_token")