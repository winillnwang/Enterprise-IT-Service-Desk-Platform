from rest_framework import serializers

from accounts.models import (
    Department,
    User,
)
from .models import Asset
from drf_spectacular.utils import (
    extend_schema_field,
    inline_serializer,
)


class AssetSerializer(serializers.ModelSerializer):
    assigned_to = serializers.SerializerMethodField()

    assigned_to_id = serializers.PrimaryKeyRelatedField(
        source="assigned_to",
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    department = serializers.SerializerMethodField()

    department_id = serializers.PrimaryKeyRelatedField(
        source="department",
        queryset=Department.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Asset

        fields = [
            "id",
            "asset_no",
            "name",
            "asset_type",
            "serial_number",
            "status",
            "assigned_to",
            "assigned_to_id",
            "department",
            "department_id",
            "purchase_date",
            "warranty_end",
            "notes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        current_status = (
            self.instance.status
            if self.instance
            else Asset.Status.AVAILABLE
        )

        current_assigned_to = (
            self.instance.assigned_to
            if self.instance
            else None
        )

        new_status = attrs.get(
            "status",
            current_status,
        )

        new_assigned_to = attrs.get(
            "assigned_to",
            current_assigned_to,
        )

        # CREATE：
        # 新增資產時，如果指定使用者，
        # 而狀態是 available，
        # 自動改成 in_use。
        if (
            self.instance is None
            and new_assigned_to is not None
            and new_status == Asset.Status.AVAILABLE
        ):
            attrs["status"] = Asset.Status.IN_USE
            new_status = Asset.Status.IN_USE

        # UPDATE：
        # 如果只修改 assigned_to，
        # 沒有手動修改 status，
        # 則自動同步狀態。
        if (
            self.instance is not None
            and "assigned_to" in attrs
            and "status" not in attrs
        ):
            if new_assigned_to is not None:
                attrs["status"] = Asset.Status.IN_USE
                new_status = Asset.Status.IN_USE

            elif current_status == Asset.Status.IN_USE:
                attrs["status"] = Asset.Status.AVAILABLE
                new_status = Asset.Status.AVAILABLE

        # available 不可以有使用者
        if (
            new_status == Asset.Status.AVAILABLE
            and new_assigned_to is not None
        ):
            raise serializers.ValidationError({
                "assigned_to_id":
                    "Available assets cannot have an assigned user."
            })

        # in_use 一定要有使用者
        if (
            new_status == Asset.Status.IN_USE
            and new_assigned_to is None
        ):
            raise serializers.ValidationError({
                "assigned_to_id":
                    "In-use assets must have an assigned user."
            })

        # retired 不可以仍然指派給使用者
        if (
            new_status == Asset.Status.RETIRED
            and new_assigned_to is not None
        ):
            raise serializers.ValidationError({
                "assigned_to_id":
                    "Retired assets cannot have an assigned user."
            })

        return attrs

    @extend_schema_field(
        inline_serializer(
            name="AssetAssignedUser",
            fields={
                "id": serializers.IntegerField(),
                "username": serializers.CharField(),
                "role": serializers.CharField(),
            },
            allow_null=True,
        )
    )

    def get_assigned_to(self, obj):
        if obj.assigned_to is None:
            return None

        return {
            "id": obj.assigned_to.id,
            "username": obj.assigned_to.username,
            "role": obj.assigned_to.role,
        }

    @extend_schema_field(
        inline_serializer(
            name="AssetDepartment",
            fields={
                "id": serializers.IntegerField(),
                "code": serializers.CharField(),
                "name": serializers.CharField(),
            },
            allow_null=True,
        )
    )

    def get_department(self, obj):
        if obj.department is None:
            return None

        return {
            "id": obj.department.id,
            "code": obj.department.code,
            "name": obj.department.name,
        }
