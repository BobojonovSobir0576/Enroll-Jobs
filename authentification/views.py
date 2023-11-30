from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
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
    LoginSerializer,
    LogoutSerializer,
    UserProfileSerializer,
    CreateAdminHrSerializer,
    UserDetailSerializers,
    PasswordResetSerializer,
    PasswordResetCompleteSerializer
)

from enrolls.utils import (
    Util,
    PasswordReset
)

def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "accsess": str(refresh.access_token)}

class RolesViews(APIView):

    def get(self, request):
        queryset = Group.objects.all()[0:2]
        serializer = RolesSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateAdminHrViews(APIView):

    def get(self, request):
        quryset = User.objects.prefetch_related("groups").filter(
            Q(groups__name__in=["Hr"])
        )
        serializer = UserProfileSerializer(quryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=None, responses=CreateAdminHrSerializer)
    def post(self, request):
        serializers = CreateAdminHrSerializer(data=request.data, partial=True)
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(APIView):
    @extend_schema(request=None, responses=LoginSerializer)
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

    @extend_schema(request=None, responses=UserDetailSerializers)
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

    @extend_schema(request=None, responses=UserDetailSerializers)
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


class RequestPasswordRestEmail(generics.GenericAPIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    serializer_class = PasswordResetSerializer

    @extend_schema(request=None, responses=PasswordResetSerializer)
    def post(self, request):
        serializers = self.serializer_class(data=request.data)

        email = request.data.get('email')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
            absurl = 'http://' + current_site + relativeLink
            email_body = f'Hi \n Use link below to reset password \n link: {absurl}'
            data = {
                'email_body': email_body,
                'to_email': user.email,
                'email_subject': 'Reset your password'
            }

            Util.send(data)
        return Response({'success':'We have sent you to rest your password'}, status=status.HTTP_200_OK)


class PasswordTokenCheckView(generics.GenericAPIView):
    serializer_class = UserProfileSerializer

    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error':'Token is not valid, Please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True, 'msg':'Credential Valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError:
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error':'Token is not valid, Please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordView(generics.GenericAPIView):
    serializer_class = PasswordResetCompleteSerializer

    @extend_schema(request=None, responses=PasswordResetCompleteSerializer)
    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'success'}, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(request=None, responses=LogoutSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
