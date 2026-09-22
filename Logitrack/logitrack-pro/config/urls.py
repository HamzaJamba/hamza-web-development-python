from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    path("api/roles/", include("roles.urls")),
    path("api/shipments/", include("shipments.urls")),
    path("api/fleet/", include("fleet.urls")),
    path("api/drivers/", include("drivers.urls")),
    path("api/warehouses/", include("warehouses.urls")),
    path("api/inventory/", include("inventory.urls")),
    path("api/routes/", include("routes.urls")),
    path("api/incidents/", include("incidents.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/tracking/", include("tracking.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/reports/", include("reports.urls")),
    path("api/audit/", include("audit.urls")),

    # API docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # runserver auto-serves static files in DEBUG, but daphne (ASGI) doesn't —
    # add it explicitly so admin/DRF-browsable-API CSS loads when using daphne.
    urlpatterns += staticfiles_urlpatterns()
