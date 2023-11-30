from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status, views, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q


from authentification.renderers import UserRenderers

from enrolls.utils import Util


from enrolls.models import (
    JobCategories,
    JobVacancies,
    JobApply,
    StatusApply
)

from enrolls.models import JobCategories, JobVacancies, JobApply


from enrolls.serializers import (
    JobApplySerializer,
    JobCategoriesListSerializer,

    JobVacanciesSerializer,
    JobVacanciesListSerializer,
    JobApplyListSerilaizer,
)

from chat.models import (
    Conversation
)


from enrolls.pagination import StandardResultsSetPagination

import string, random


def password_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


class JobCategoriesView(APIView):
    def get(self, request):
        quryset = JobCategories.objects.all()
        serializer = JobCategoriesListSerializer(quryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses=JobCategoriesListSerializer)
    def post(self, request):
        serializer = JobCategoriesListSerializer(data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class JobCategoriesDetailsView(APIView):
    def get(self, request, id):
        queryset = get_object_or_404(JobCategories, id=id)
        serializer = JobCategoriesListSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses=JobCategoriesListSerializer)
    def put(self, request):
        serializers = JobCategoriesListSerializer(instance=request.user, data=request.data, partial=True)
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        queryset = get_object_or_404(JobCategories, id=id)
        queryset.delete()
        return Response({'message': 'deleted successfully'}, status=status.HTTP_200_OK)


class JobVacanciesView(APIView):
    def get(self, request):
        quryset = JobVacancies.objects.all()
        serializer = JobVacanciesListSerializer(quryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses=JobVacanciesSerializer)
    def post(self, request):
        serializer = JobVacanciesSerializer(data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobVacanciesDetailsView(APIView):
    def get(self, request, id):
        queryset = get_object_or_404(JobVacancies, id=id)
        serializer = JobVacanciesListSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses=JobVacanciesSerializer)
    def put(self, request):
        serializers = JobVacanciesSerializer(instance=request.user, data=request.data, partial=True)
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        queryset = get_object_or_404(JobVacancies, id=id)
        queryset.delete()
        return Response({'message': 'deleted successfully'}, status=status.HTTP_200_OK)


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
    def get(self, request, pk):
        queryset = get_object_or_404(JobVacancies, id=pk)
        serializer = JobVacanciesListSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses=JobVacanciesSerializer)
    def put(self, request):
        serializers = JobVacanciesSerializer(
            instance=request.user, data=request.data, partial=True
        )
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        queryset = get_object_or_404(JobVacancies, id=pk)
        queryset.delete()
        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)



class AppllyJobView(APIView):
    def get(self, request):
        queryset = JobApply.objects.all().order_by("-id")
        serializer = JobApplyListSerilaizer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses=JobApplySerializer)
    def post(self, request):
        # filter_user = User.objects.filter(
        #     Q(username=request.data.get("username"))
        #     | Q(email=request.data.get("email"))
        # )
        # if filter_user:
        #     return Response({"msg": "This username or email is already exists.."})
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


class RejectAcceptsView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    @extend_schema(request=None, responses=JobApplyListSerilaizer)
    def get(self, request, id, status_id):
        queryset = get_object_or_404(JobApply, id=id)
        get_status = status_id
        get_status_id = StatusApply.objects.filter(
            Q(id=get_status)
        ).first()
        if get_status_id.name == 'Accept':

            queryset.jobs_status = get_status_id
            queryset.save()

            get_password = password_generator()
            user = authenticate(username=queryset.user.username, password=queryset.user.password)

            check_msg_channels = Conversation.objects.select_related('receiver').filter(
                Q(receiver=queryset.user)
            ).select_related('jobs').filter(
                Q(jobs=queryset.jobs)
            )

            if not user and bool(check_msg_channels) == False:

                filter_user = User.objects.filter(
                        Q(username=queryset.user.username)
                    ).update(password=make_password(get_password))

                create_channels = Conversation.objects.create(
                    initiator=request.user,
                )
                create_channels.receiver = queryset.user
                create_channels.jobs = queryset.jobs
                create_channels.save()

                email_body = (f'Hi {queryset.user.username}, There your password to enter using login. \n Password: {get_password} \n'
                              f'New channel created by {create_channels.initiator.first_name} {create_channels.initiator.last_name}'
                              f' vs {create_channels.receiver.first_name} {create_channels.receiver.lastname}')

                data = {
                    'email_body': email_body,
                    'to_email': queryset.user.email,
                    'email_subject': 'Accept job'
                }

                Util.send(data)

                serializer = JobApplyListSerilaizer(queryset)
                return Response(serializer.data, status=status.HTTP_200_OK)

            create_channels = Conversation.objects.create(
                initiator=request.user,
            )
            create_channels.receiver = queryset.user
            create_channels.jobs = queryset.jobs
            create_channels.save()

            email_body = (f'Hi {queryset.user.username}, For you created new channel to conversation {queryset.jobs.title} \n'
                          f'New channel created by {create_channels.initiator.first_name} {create_channels.initiator.last_name}'
                          f' vs {create_channels.receiver.first_name} {create_channels.receiver.last_name}')

            data = {
                'email_body': email_body,
                'to_email': queryset.user.email,
                'email_subject': 'Reject job'
            }

            Util.send(data)

            serializer = JobApplyListSerilaizer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)

        email_body = f'Hi {queryset.user.username}, Sorry you are rejected by {queryset.jobs.title}'

        data = {
            'email_body': email_body,
            'to_email': queryset.user.email,
            'email_subject': 'Reject job'
        }

        Util.send(data)


        serializer = JobApplyListSerilaizer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ApplyJobDetailsView(APIView):
    @extend_schema(request=None, responses=JobApplyListSerilaizer)
    def get(self, request, id):
        queryset = get_object_or_404(JobApply, id=id)
        serializer = JobApplyListSerilaizer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        queryset = get_object_or_404(JobApply, id=id)
        queryset.delete()
        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)



