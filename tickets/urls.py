from django.urls import path

from .views import (
    TicketCategoryListAPIView,
    TicketDetailAPIView,
    TicketHistoryListAPIView,
    TicketListCreateAPIView,
    DashboardSummaryAPIView,
    ReportSummaryAPIView,
    dashboard_page,
)

urlpatterns = [
    path(
        "ticket-categories/",
        TicketCategoryListAPIView.as_view(),
        name="ticket-category-list",
    ),
    path(
        "tickets/",
        TicketListCreateAPIView.as_view(),
        name="ticket-list-create",
    ),
    path(
        "tickets/<int:pk>/",
        TicketDetailAPIView.as_view(),
        name="ticket-detail",
    ),
    path(
        "tickets/<int:pk>/history/",
        TicketHistoryListAPIView.as_view(),
        name="ticket-history-list",
    ),
    path(
        "dashboard/summary/",
        DashboardSummaryAPIView.as_view(),
        name="dashboard-summary",
    ),
    path(
        "reports/summary/",
        ReportSummaryAPIView.as_view(),
        name="report-summary",
    ),
]
