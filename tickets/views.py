from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated

from .models import Ticket
from .serializers import TicketSerializer

from .permissions import IsTicketOwnerOrITStaff


class TicketListCreateAPIView(ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role in ["it_engineer", "it_manager", "admin"]:
            return Ticket.objects.all().order_by("-created_at")

        return Ticket.objects.filter(reporter=user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)


class TicketDetailAPIView(RetrieveUpdateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [
        IsAuthenticated,
        IsTicketOwnerOrITStaff,
    ]
