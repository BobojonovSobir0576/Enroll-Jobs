from rest_framework import generics, permissions, status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import update_session_auth_hash

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
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

from authentification.renderers import UserRenderers

from authentification.serializers import (
    RolesSerializer,
    UserSignUpSerializers,
    LoginSerializer,
    LogoutSerializer,
    UserProfileSerializer,
    CreateHrSerializer,
    UserDetailSerializers,
    ChangePasswordSerializer,
)


def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "accsess": str(refresh.access_token)}


class UserSignUpViews(APIView):
    def get(self, request):
        quryset = Group.objects.all()
        serializer = RolesSerializer(quryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSignUpSerializers(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateHrViews(APIView):
    def get(self, request):
        quryset = User.objects.prefetch_related("groups").filter(
            Q(groups__name__in=["hr"])
        )
        serializer = UserProfileSerializer(quryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializers = CreateHrSerializer(data=request.data, partial=True)
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(APIView):
    def post(self, request, format=None):
        serializers = LoginSerializer(data=request.data, partial=True)
        if serializers.is_valid(raise_exception=True):
            username = request.data.get("username", "")
            password = request.data.get("password", "")

            if username == "" and password == "":
                return Response(
                    {
                        "error": {
                            "none_filed_error": ["Username or password is not write"]
                        }
                    },
                    status=status.HTTP_204_NO_CONTENT,
                )
            user = authenticate(username=username, password=password)

            if not user:
                return Response(
                    {"error": ("Invalid credentials, try again")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = get_token_for_user(user)
            return Response({"token": token}, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfilesView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    def get(self, request, format=None):
        serializers = UserProfileSerializer(request.user)
        return Response({"msg": serializers.data}, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    serializers = UserDetailSerializers

    def put(self, request):
        serializers = self.serializers(
            instance=request.user, data=request.data, partial=True
        )
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        queryset = request.user.delete()
        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)


class HrDetailsView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    serializers = UserDetailSerializers

    def get(self, request, id):
        quryset = User.objects.prefetch_related("groups").filter(
            Q(groups__name__in=["hr"])
        )
        serializer = UserProfileSerializer(quryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        queryset = get_object_or_404(User, id=id)
        serializers = self.serializers(
            instance=queryset, data=request.data, partial=True
        )
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        queryset = get_object_or_404(User, id=id)
        queryset.delete()
        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    if request.method == "POST":
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get("old_password")):
                user.set_password(serializer.data.get("new_password"))
                user.save()
                update_session_auth_hash(request, user)
                return Response(
                    {"message": "Password changed successfully."},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": "Incorrect old password."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
