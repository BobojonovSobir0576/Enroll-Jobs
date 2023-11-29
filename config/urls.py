from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt import views as jwt_views
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView
admin.site.site_url = None

urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        "token/",
        jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "token/refresh/",
        jwt_views.TokenRefreshView.as_view(), name="token_refresh"
    ),

    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        TemplateView.as_view(
            template_name="doc.html", extra_context={"schema_url": "api_schema"}
        ),
        name="swagger-ui",
    ),
    
    path('api/auth/', include('authentification.urls')),
    path('api/job/', include('enrolls.urls')),
    path(
        "api/password_reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset")),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {
            "document_root": settings.MEDIA_ROOT,
        },
    ),
]