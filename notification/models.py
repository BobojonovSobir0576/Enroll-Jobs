from django.db import models
from django.contrib.auth.models import User
from chat.models import Message


NOTIFICATION_TYPES = (
    ('MESSAGE_SENT', 'MESSAGE_SENT'),
    ('MESSAGE_ACCEPT', 'MESSAGE_ACCEPT'),
)


class Notification(models.Model):
    name = models.CharField(max_length=32, choices=NOTIFICATION_TYPES)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    message = models.CharField(max_length=255, null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return self.name