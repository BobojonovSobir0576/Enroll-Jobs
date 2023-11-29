from django.urls import  path
from notification.views.views import (
    NotificatioView,
    NotificationsViews
)

urlpatterns = [
    path('', NotificationsViews.as_view())
]