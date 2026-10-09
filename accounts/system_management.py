from django.shortcuts import render

from rest_framework import serializers
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
)

from accounts.models import (
    Department,
    User,
)
from tickets.models import TicketCategory


class IsSystemManager(BasePermission):
    def has_permission(
        self,
        request,
        view,
    ):
        return request.user.is_authenticated and request.user.role in [
            User.Role.IT_MANAGER,
            User.Role.ADMIN,
        ]


class SystemDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            "id",
            "code",
            "name",
            "description",
        ]

        read_only_fields = [
            "id",
        ]


class SystemUserSerializer(serializers.ModelSerializer):
    department = SystemDepartmentSerializer(
        read_only=True,
    )

    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source="department",
        write_only=True,
        required=False,
        allow_null=True,
    )

    password = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
    )

    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "department",
            "department_id",
            "is_active",
            "password",
        ]

        read_only_fields = [
            "id",
        ]

    def validate(self, attrs):
        if self.instance is None and not attrs.get("password"):
            raise serializers.ValidationError(
                {"password": ("Password is required " "when creating a user.")}
            )

        return attrs

    def create(
        self,
        validated_data,
    ):
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        return user

    def update(
        self,
        instance,
        validated_data,
    ):
        password = validated_data.pop(
            "password",
            None,
        )

        instance = super().update(
            instance,
            validated_data,
        )

        if password:
            instance.set_password(password)

            instance.save(
                update_fields=[
                    "password",
                ]
            )

        return instance


class SystemTicketCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCategory

        fields = [
            "id",
            "code",
            "name",
            "description",
            "is_active",
        ]

        read_only_fields = [
            "id",
        ]


class SystemUserListCreateAPIView(ListCreateAPIView):
    serializer_class = SystemUserSerializer

    permission_classes = [
        IsAuthenticated,
        IsSystemManager,
    ]

    def get_queryset(self):
        return User.objects.select_related("department").order_by("username")


class SystemUserDetailAPIView(RetrieveUpdateAPIView):
    serializer_class = SystemUserSerializer

    permission_classes = [
        IsAuthenticated,
        IsSystemManager,
    ]

    def get_queryset(self):
        return User.objects.select_related("department")


class SystemDepartmentListCreateAPIView(ListCreateAPIView):
    serializer_class = SystemDepartmentSerializer

    permission_classes = [
        IsAuthenticated,
        IsSystemManager,
    ]

    def get_queryset(self):
        return Department.objects.order_by("code")


class SystemDepartmentDetailAPIView(RetrieveUpdateAPIView):
    serializer_class = SystemDepartmentSerializer

    permission_classes = [
        IsAuthenticated,
        IsSystemManager,
    ]

    def get_queryset(self):
        return Department.objects.all()


class SystemTicketCategoryListCreateAPIView(ListCreateAPIView):
    serializer_class = SystemTicketCategorySerializer

    permission_classes = [
        IsAuthenticated,
        IsSystemManager,
    ]

    def get_queryset(self):
        return TicketCategory.objects.all().order_by("code")


class SystemTicketCategoryDetailAPIView(RetrieveUpdateAPIView):
    serializer_class = SystemTicketCategorySerializer

    permission_classes = [
        IsAuthenticated,
        IsSystemManager,
    ]

    def get_queryset(self):
        return TicketCategory.objects.all()


def system_management_page(request):
    return render(
        request,
        "accounts/system_management.html",
    )
