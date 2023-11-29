from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.shortcuts import get_object_or_404

from authentification.renderers import (
    UserRenderers
)

from authentification.serializers import (
    LoginSerializer,
    LogoutSerializer,
    UserProfileSerializer,
    CreateAdminHrSerializer,
    UserDetailSerializers,
    RolesSerializer
)


def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'accsess': str(refresh.access_token)
    }


class RolesViews(APIView):

    def get(self, request):
        queryset = Group.objects.all()[0:2]
        serializer = RolesSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateAdminHrViews(APIView):

    def get(self, request):
        quryset = User.objects.prefetch_related('groups').filter(
            Q(groups__name__in=['Hr'])
        )
        serializer = UserProfileSerializer(quryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializers = CreateAdminHrSerializer(data=request.data, partial=True)
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(APIView):
    def post(self,request,format=None):
        serializers = LoginSerializer(data=request.data, partial=True)
        if serializers.is_valid(raise_exception=True):
            username = request.data.get('username', '')
            password = request.data.get('password', '')

            if username == '' and password == '':
                return Response({'error': {'none_filed_error': ['Username or password is not write']}},status=status.HTTP_204_NO_CONTENT)
            user = authenticate(username=username, password=password)

            if not user:
                return Response({'error': ('Invalid credentials, try again')}, status=status.HTTP_400_BAD_REQUEST)
            token = get_token_for_user(user)
            return Response({'token':token},status=status.HTTP_200_OK)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)



class UserProfilesView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]

    def get(self, request, format=None):
        serializers = UserProfileSerializer(request.user)
        return Response({'msg': serializers.data}, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    serializers = UserDetailSerializers

    def put(self, request):
        serializers = self.serializers(instance=request.user, data=request.data, partial=True)
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        queryset = request.user.delete()
        return Response({'message': 'deleted successfully'}, status=status.HTTP_200_OK)


class HrDetailsView(APIView):
    render_classes = [UserRenderers]
    perrmisson_class = [IsAuthenticated]
    serializers = UserDetailSerializers

    def put(self, request, id):
        queryset = get_object_or_404(User, id=id)
        serializers = self.serializers(instance=queryset, data=request.data, partial=True)
        if serializers.is_valid(raise_exception=True):
            serializers.save()
            return Response(serializers.data, status=status.HTTP_200_OK)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        queryset = get_object_or_404(User, id=id)
        queryset.delete()
        return Response({'message': 'deleted successfully'}, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)