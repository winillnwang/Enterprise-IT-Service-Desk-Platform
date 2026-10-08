from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
)
from .models import (
    Ticket,
    TicketCategory,
    TicketHistory,
)
from .serializers import (
    TicketCategorySerializer,
    TicketHistorySerializer,
    TicketSerializer,
)

from .permissions import IsTicketOwnerOrITStaff


from django.shortcuts import render


class TicketCategoryListAPIView(ListAPIView):
    serializer_class = TicketCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TicketCategory.objects.filter(is_active=True).order_by("name")


class TicketListCreateAPIView(ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role in ["it_engineer", "it_manager", "admin"]:
            queryset = Ticket.objects.all()
        else:
            queryset = Ticket.objects.filter(
                reporter=user
            )

        status = self.request.query_params.get("status")
        priority = self.request.query_params.get("priority")
        search = self.request.query_params.get("search")

        if status:
            queryset = queryset.filter(
                status=status
            )

        if priority:
            queryset = queryset.filter(
                priority=priority
            )

        if search:
            queryset = queryset.filter(
                title__icontains=search
            )

        return queryset.order_by("-created_at")


class TicketDetailAPIView(RetrieveUpdateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [
        IsAuthenticated,
        IsTicketOwnerOrITStaff,
    ]


class TicketHistoryListAPIView(ListAPIView):
    serializer_class = TicketHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ticket_id = self.kwargs["pk"]
        user = self.request.user

        if user.role in [
            "it_engineer",
            "it_manager",
            "admin",
        ]:
            return TicketHistory.objects.filter(ticket_id=ticket_id).order_by(
                "-created_at"
            )

        return TicketHistory.objects.filter(
            ticket_id=ticket_id,
            ticket__reporter=user,
        ).order_by("-created_at")


def ticket_list_page(request):
    return render(request, "tickets/ticket_list.html")

def ticket_create_page(request):
    return render(request, "tickets/ticket_create.html")

def ticket_detail_page(request, pk):
    return render(
        request,
        "tickets/ticket_detail.html",
        {"ticket_id": pk},
    )


class DashboardSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: inline_serializer(
                name="DashboardSummaryResponse",
                fields={
                    "total_tickets": serializers.IntegerField(),
                    "open_tickets": serializers.IntegerField(),
                    "in_progress_tickets": serializers.IntegerField(),
                    "resolved_tickets": serializers.IntegerField(),
                    "priority_distribution": serializers.DictField(
                        child=serializers.IntegerField(),
                    ),
                    "status_distribution": serializers.DictField(
                        child=serializers.IntegerField(),
                    ),
                },
            ),
            403: inline_serializer(
                name="DashboardPermissionDeniedResponse",
                fields={
                    "success": serializers.BooleanField(),
                    "message": serializers.CharField(),
                },
            ),
        },
    )
    def get(self, request):
        if request.user.role not in [
            "it_engineer",
            "it_manager",
            "admin",
        ]:
            return Response(
                {
                    "success": False,
                    "message": "You do not have permission to access the dashboard.",
                },
                status=403,
            )

        queryset = Ticket.objects.all()

        data = {
            "total_tickets": queryset.count(),
            "open_tickets": queryset.filter(status=Ticket.Status.OPEN).count(),
            "in_progress_tickets": queryset.filter(
                status=Ticket.Status.IN_PROGRESS
            ).count(),
            "resolved_tickets": queryset.filter(status=Ticket.Status.RESOLVED).count(),
            "priority_distribution": {
                "low": queryset.filter(priority=Ticket.Priority.LOW).count(),
                "medium": queryset.filter(priority=Ticket.Priority.MEDIUM).count(),
                "high": queryset.filter(priority=Ticket.Priority.HIGH).count(),
                "critical": queryset.filter(priority=Ticket.Priority.CRITICAL).count(),
            },
            "status_distribution": {
                "open": queryset.filter(status=Ticket.Status.OPEN).count(),
                "assigned": queryset.filter(status=Ticket.Status.ASSIGNED).count(),
                "in_progress": queryset.filter(
                    status=Ticket.Status.IN_PROGRESS
                ).count(),
                "resolved": queryset.filter(status=Ticket.Status.RESOLVED).count(),
                "closed": queryset.filter(status=Ticket.Status.CLOSED).count(),
            },
        }

        return Response(data)


def dashboard_page(request):
    return render(
        request,
        "tickets/dashboard.html",
    )
