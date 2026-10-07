from rest_framework import serializers

from .models import (
    Department,
    User,
)

class CurrentUserSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "department",
        ]


class ITStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "role",
        ]


class AssetAssigneeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "role",
        ]


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [
            "id",
            "code",
            "name",
        ]
