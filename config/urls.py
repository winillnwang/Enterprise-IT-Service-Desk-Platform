"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from accounts.views import (
    CurrentUserAPIView,
    ITStaffListAPIView,
    AssetAssigneeListAPIView,
    DepartmentListAPIView,
)

from tickets.views import (
    ticket_create_page,
    ticket_detail_page,
    ticket_list_page,
    dashboard_page,
)

from assets.views import (
    asset_list_page,
    asset_detail_page,
    asset_create_page,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/auth/login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/auth/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "api/auth/me/",
        CurrentUserAPIView.as_view(),
        name="current-user",
    ),
    path(
        "api/users/it-staff/",
        ITStaffListAPIView.as_view(),
        name="it-staff-list",
    ),
    path("api/", include("tickets.urls")),
    path("", include("accounts.urls")),
    path(
        "tickets/",
        ticket_list_page,
        name="ticket-list-page",
    ),
    path(
        "tickets/create/",
        ticket_create_page,
        name="ticket-create-page",
    ),
    path(
        "tickets/<int:pk>/",
        ticket_detail_page,
        name="ticket-detail-page",
    ),
    path(
        "dashboard/",
        dashboard_page,
        name="dashboard-page",
    ),
    path(
        "api/",
        include("assets.urls"),
    ),
    path(
        "assets/",
        asset_list_page,
        name="asset-list-page",
    ),
    path(
        "assets/create/",
        asset_create_page,
        name="asset-create-page",
    ),
    path(
        "assets/<int:pk>/",
        asset_detail_page,
        name="asset-detail-page",
    ),
    path(
        "api/users/asset-assignees/",
        AssetAssigneeListAPIView.as_view(),
        name="asset-assignee-list",
    ),
    path(
        "api/departments/",
        DepartmentListAPIView.as_view(),
        name="department-list",
    ),
]
