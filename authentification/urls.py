from django.urls import path

from authentification.views import (
    LoginApiView,
    UserProfilesView,
    UserDetailView,
    LogoutView,
    CreateAdminHrViews,
    HrDetailsView,
    RolesViews,
    RequestPasswordRestEmail,
    PasswordTokenCheckView,
    SetNewPasswordView
)


urlpatterns = [
    path('roles/', RolesViews.as_view()),
    path('create-admin-hr/', CreateAdminHrViews.as_view()),
    path('update-hr/<int:id>/', HrDetailsView.as_view()),
    path('request-rest-email-by-email/', RequestPasswordRestEmail.as_view()),
    path('password-reset-by-email/<uidb64>/<token>/', PasswordTokenCheckView.as_view(),),
    path('reset_password_complete-by-email/', SetNewPasswordView.as_view()),
    path('login/', LoginApiView.as_view()),
    path('profile/', UserProfilesView.as_view()),
    path('update-profile/', UserDetailView.as_view()),
    path('logout/', LogoutView.as_view()),
]
