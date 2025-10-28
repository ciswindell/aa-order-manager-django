"""API URL Configuration."""

from api.views.auth import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    logout_view,
    user_profile_view,
)
from api.views.dashboard import dashboard_view
from api.views.integrations import (
    basecamp_callback,
    connect_basecamp,
    connect_dropbox,
    disconnect_basecamp,
    disconnect_dropbox,
    dropbox_callback,
    get_integration_status,
)
from api.views.leases import LeaseViewSet
from api.views.orders import OrderViewSet
from api.views.reports import ReportViewSet
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = "api"

# Create router for viewsets
router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"reports", ReportViewSet, basename="report")
router.register(r"leases", LeaseViewSet, basename="lease")

urlpatterns = [
    # Authentication endpoints
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", logout_view, name="logout"),
    path("auth/user/", user_profile_view, name="user_profile"),
    # Dashboard endpoints
    path("dashboard/", dashboard_view, name="dashboard"),
    # Integration endpoints
    path("integrations/status/", get_integration_status, name="integration_status"),
    path("integrations/dropbox/connect/", connect_dropbox, name="dropbox_connect"),
    path(
        "integrations/dropbox/callback/",
        dropbox_callback,
        name="dropbox_callback",
    ),
    path(
        "integrations/dropbox/disconnect/",
        disconnect_dropbox,
        name="dropbox_disconnect",
    ),
    path("integrations/basecamp/connect/", connect_basecamp, name="basecamp_connect"),
    path(
        "integrations/basecamp/callback/",
        basecamp_callback,
        name="basecamp_callback",
    ),
    path(
        "integrations/basecamp/disconnect/",
        disconnect_basecamp,
        name="basecamp_disconnect",
    ),
    # Include router URLs
    path("", include(router.urls)),
]
