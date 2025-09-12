from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from accounts.urls import auth_urlpatterns, user_urlpatterns
from shared.views import ProtectedAudioStreamView, ProtectedAudioDownloadView
from . import settings


class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema


schema_view = get_schema_view(
    openapi.Info(
        title="Xazna Swagger",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    generator_class=BothHttpAndHttpsSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

base_patterns = [
    path("auth/", include(auth_urlpatterns)),
    path("user/", include(user_urlpatterns)),
    path("tts/", include("tts.urls")),
    path("stt/", include("stt.urls")),
]
protected_media_patterns = [
    path("audio/stream/<id>/", ProtectedAudioStreamView.as_view(), name="audio_stream"),
    path("audio/download/<id>/", ProtectedAudioDownloadView.as_view(), name="audio_download")
]

urlpatterns = [
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema_swagger_ui"),
    path("api/", include(base_patterns)),
    path("admin/", admin.site.urls),
    path("protected/media/", include(protected_media_patterns)),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
