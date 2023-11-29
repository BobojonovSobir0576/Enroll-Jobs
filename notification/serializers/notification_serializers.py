from rest_framework import serializers

from notification.models import Notification

from authentification.serializers import (
    UserProfileSerializer
)

class NotificationSerializer(serializers.ModelSerializer):
    sender = UserProfileSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'sender',
            'message',
            'sent_at'
        ]