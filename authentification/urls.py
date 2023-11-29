from django.urls import path

from authentification.views import (
    LoginApiView,
    UserProfilesView,
    UserDetailView,
    LogoutView,
    CreateHrViews,
    HrDetailsView
)


urlpatterns = [
    path('create-hr/', CreateHrViews.as_view()),
    path('login/', LoginApiView.as_view(), name='login'),
    path('profile/', UserProfilesView.as_view(), name='profile'),
    path('update/', UserDetailView.as_view(), name='update'),
    path('update-hr/<int:id>/', HrDetailsView.as_view()),
    path('logout/', LogoutView.as_view(), name='logout'),
]
