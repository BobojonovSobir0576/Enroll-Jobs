from rest_framework import generics, permissions, status, views, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import (
    force_str,
    smart_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from django.db.models import Q

from authentification.renderers import UserRenderers

from enrolls.utils import Util

from enrolls.models import JobCategories, JobVacancies, JobApply

from enrolls.serializers import (
    JobApplySerializer,
    JobCategoriesListSerializer,
    JobCategoriesCrudSerializer,
    JobVacanciesSerializer,
    JobVacanciesListSerializer,
    JobApplyListSerilaizer,
)
from enrolls.pagination import StandardResultsSetPagination
import string, random


def password_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


# -------------
class JobCategoriesView(APIView):
    def get(self, request):
        quryset = JobCategories.objects.all()
        serializer = JobCategoriesListSerializer(quryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = JobCategoriesCrudSerializer(data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobCategoryCrudViews(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    def get(self, request, pk):
        objects_list = JobCategories.objects.filter(id=pk)
        jobs = JobVacancies.objects.filter(job_category=pk).count()
        serializers = JobCategoriesListSerializer(objects_list, many=True)
        return Response({'tag': serializers.data, 'vankt_count': jobs}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        serializers = JobCategoriesCrudSerializer(
            instance=JobCategories.objects.filter(id=pk)[0],
            data=request.data,
            partial=True,
        )
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(
            {"error": "update error data"}, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        objects_get = JobCategories.objects.get(id=pk)
        objects_get.delete()
        return Response({"message": "Delete success"}, status=status.HTTP_200_OK)


# -------------
# -------------
class JobVacanciesView(APIView):
    def get(self, request):
        quryset = JobVacancies.objects.all()
        serializer = JobVacanciesListSerializer(quryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = JobVacanciesSerializer(data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobVacanciesAllView(APIView):
    pagination_class = StandardResultsSetPagination
    serializer_class = JobVacanciesListSerializer

    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        else:
            pass
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def get(self, request, format=None, *args, **kwargs):
        instance = JobVacancies.objects.all().order_by("-id")
        page = self.paginate_queryset(instance)
        if page is not None:
            serializer = self.get_paginated_response(
                self.serializer_class(page, many=True).data
            )
        else:
            serializer = self.serializer_class(instance, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)


class JobVacanciesDetailsView(APIView):
    def get(self, request, id):
        queryset = get_object_or_404(JobVacancies, id=id)
        serializer = JobVacanciesListSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializers = JobVacanciesSerializer(
            instance=request.user, data=request.data, partial=True
        )
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        queryset = get_object_or_404(JobVacancies, id=id)
        queryset.delete()
        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)


# -------------


# -------------
class AppllyJobView(APIView):
    def get(self, request):
        queryset = JobApply.objects.all().order_by("-id")
        serializer = JobApplyListSerilaizer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        filter_user = User.objects.filter(
            Q(username=request.data.get("username"))
            | Q(email=request.data.get("email"))
        )
        if filter_user:
            return Response({"msg": "This username or email is already exists.."})
        serializer = JobApplySerializer(
            data=request.data,
            partial=True,
            context={
                "username": request.data.get("username"),
                "email": request.data.get("email"),
            },
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplySearchView(generics.ListAPIView):
    queryset = JobApply.objects.all()
    serializer_class = JobApplyListSerilaizer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "user__username",
    ]

    def get(self, request, format=None):
        search_name = request.query_params.get("search", "")
        product = JobApply.objects.filter((Q(user__username__icontains=search_name)))
        serializers = self.serializer_class(product, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class ApplyJobDetailsView(APIView):
    def get(self, request, id):
        queryset = get_object_or_404(JobApply, id=id)
        serializer = JobApplyListSerilaizer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        queryset = get_object_or_404(JobApply, id=id)
        queryset.delete()
        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)


# -------------
