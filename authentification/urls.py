from django.urls import path

from authentification.views import (
    LoginApiView,
    UserProfilesView,
    UserDetailView,
    LogoutView,
    CreateAdminHrViews,
    HrDetailsView,
    RolesViews
)


urlpatterns = [
    path('roles/', RolesViews.as_view()),
    path('create-admin-hr/', CreateAdminHrViews.as_view()),
    path('update-hr/<int:id>/', HrDetailsView.as_view()),

    path('login/', LoginApiView.as_view(), name='login'),
    path('profile/', UserProfilesView.as_view(), name='profile'),
    path('update-profile/', UserDetailView.as_view(), name='update'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
