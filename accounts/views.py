from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from .models import (
    Department,
    User,
)
from .serializers import (
    CurrentUserSerializer,
    ITStaffSerializer,
    AssetAssigneeSerializer,
    DepartmentSerializer,
)

def login_page(request):
    return render(request, "accounts/login.html")


class CurrentUserAPIView(RetrieveAPIView):
    serializer_class = CurrentUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ITStaffListAPIView(ListAPIView):
    serializer_class = ITStaffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            role__in=[
                User.Role.IT_ENGINEER,
                User.Role.IT_MANAGER,
                User.Role.ADMIN,
            ]
        ).order_by("username")


class AssetAssigneeListAPIView(ListAPIView):
    serializer_class = AssetAssigneeSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        user = self.request.user

        if user.role not in [
            "it_engineer",
            "it_manager",
            "admin",
        ]:
            return User.objects.none()

        return User.objects.filter(
            is_active=True,
        ).order_by("username")


class DepartmentListAPIView(ListAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):
        user = self.request.user

        if user.role not in [
            "it_engineer",
            "it_manager",
            "admin",
        ]:
            return Department.objects.none()

        return Department.objects.all().order_by("code")
