from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from studio.frontend import api_config_js, serve_student_frontend

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("studio.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path(
        "docs",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui-no-slash",
    ),
]

if settings.DEBUG and settings.SERVE_FRONTEND:
    urlpatterns += [
        path("config.js", api_config_js, name="api-config-js"),
        path(
            "favicon.svg",
            serve_student_frontend,
            {"path": "favicon.svg"},
            name="favicon-svg",
        ),
        path("", serve_student_frontend, name="frontend-index"),
        re_path(
            r"^(?P<path>[\w\-\./]+\.(?:html|js|css|svg|ico|png|webp))$",
            serve_student_frontend,
            name="frontend-asset",
        ),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
