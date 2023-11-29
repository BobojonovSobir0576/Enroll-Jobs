from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.shortcuts import redirect, reverse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from notification.models import (
    Notification
)
from  notification.serializers.notification_serializers import (
    NotificationSerializer
)

from authentification.renderers import UserRenderers

class NotificationsViews(APIView):

    def get(self, request):
        queryset = Notification.objects.select_related('sender').filter(
            sender=request.user
        ).filter(
            is_seen=False
        )
        serializers = NotificationSerializer(queryset, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)

class NotificatioView(APIView):

    def get(self, request):
        queryset = Notification.objects.select_related('sender').filter(
            sender=request.user
        ).filter(
            is_seen=False
        )
        serializers = NotificationSerializer(queryset, many=True)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'notification', {
                'data': {
                    "type": "chat_message",
                    "data": 'ABC'
                }
            }
        )
        return Response({'msg': 'Send Notification in Websoccet'}, status=status.HTTP_200_OK)


