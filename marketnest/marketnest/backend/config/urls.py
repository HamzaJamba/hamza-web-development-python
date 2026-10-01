from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    path("api/roles/", include("roles.urls")),
    path("api/audit/", include("audit.urls")),
    path("api/vendors/", include("vendors.urls")),
    path("api/catalog/", include("catalog.urls")),
    path("api/orders/", include("orders.urls")),
    path("api/reviews/", include("reviews.urls")),
    path("api/dashboard/", include("dashboard.urls")),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
