""" Django Libary """
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.contrib import auth
from django.utils.encoding import (
    force_str,
    smart_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import reverse

""" Django Rest Framework Libary """
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator

from enrolls.models import JobApply, JobCategories, JobVacancies, JobAttachment
from enrolls.utils import Util


import string, random


def password_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "email"]


class JobCategoriesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategories
        fields = ["id", "tag"]

    def create(self, validated_data):
        create = JobCategories.objects.create(**validated_data)
        return create

    def update(self, instance, validated_data):
        instance.tag = validated_data.get("tag", instance.tag)
        instance.save()
        return instance


class JobCategoriesCrudSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategories
        fields = ["id", "tag"]

    def create(self, validated_data):
        create = JobCategories.objects.create(**validated_data)
        return create

    def update(self, instance, validated_data):
        instance.tag = validated_data.get("tag", instance.tag)
        instance.save()
        return instance


class JobApplySerilaizer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    apply_jobs_user = UserProfileSerializer(read_only=True, many=True)

    class Meta:
        model = JobApply
        fields = ["id", "user", "jobs", "apply_jobs_user", "created_at"]


class JobVacanciesListSerializer(serializers.ModelSerializer):
    job_category = JobCategoriesListSerializer(read_only=True)
    jobs = JobApplySerilaizer(many=True, read_only=True)

    class Meta:
        model = JobVacancies
        fields = [
            "id",
            "job_category",
            "title",
            "description",
            "price",
            "jobs",
            "created_at",
        ]


class JobVacanciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobVacancies
        fields = ["id", "job_category", "title", "description", "price", "created_at"]

    def create(self, validated_data):
        create = JobVacancies.objects.create(**validated_data)
        return create

    def update(self, instance, validated_data):
        instance.title = validated_data.get("title", instance.title)
        instance.job_category = validated_data.get(
            "job_category", instance.job_category
        )
        instance.description = validated_data.get("description", instance.description)
        instance.price = validated_data.get("price", instance.price)
        instance.save()
        return instance


class JobMultipleAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAttachment
        fields = "__all__"


class JobApplyListSerilaizer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    apply_jobs_user = JobMultipleAttachmentSerializer(read_only=True, many=True)

    class Meta:
        model = JobApply
        fields = ["id", "user", "jobs", "apply_jobs_user", "created_at"]


class JobApplySerializer(serializers.ModelSerializer):
    apply_jobs_user = JobMultipleAttachmentSerializer(read_only=True, many=True)
    uploaded_files = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False, use_url=False),
        write_only=True,
    )

    class Meta:
        model = JobApply
        fields = [
            "id",
            "user",
            "jobs",
            "apply_jobs_user",
            "uploaded_files",
            "created_at",
        ]

    def create(self, validated_data):
        uploaded_files = validated_data.pop("uploaded_files")

        create_user = User.objects.create_user(
            username=self.context.get("username"), email=self.context.get("email")
        )

        get_password = password_generator()

        filter_Hr_groups = Group.objects.filter(name="User")

        create_user.set_password(get_password)
        create_user.save()

        for l in filter_Hr_groups:
            create_user.groups.add(l)
            create_user.save()

        username = self.context.get("username")
        email = self.context.get("email")
        email_body = f"Hi {username}, There your password to enter using login. \n Password: {get_password}"

        data = {
            "email_body": email_body,
            "to_email": email,
            "email_subject": "Verify your email",
        }

        Util.send(data)

        create = JobApply.objects.create(**validated_data)
        create.user = create_user
        create.save()

        for i in uploaded_files:
            JobAttachment.objects.create(job_apply=create, attachment=i)

        return create
