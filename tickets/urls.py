from django.urls import path

from .views import TicketDetailAPIView, TicketListCreateAPIView

urlpatterns = [
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
]
