from rest_framework import serializers

from accounts.models import User
from .models import (
    Ticket,
    TicketCategory,
    TicketHistory,
)

from .services import (
    create_ticket,
    update_ticket_with_history,
    validate_ticket_create,
    validate_ticket_update,
)

class TicketCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketCategory
        fields = [
            "id",
            "code",
            "name",
        ]

class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "role",
        ]


class TicketHistorySerializer(serializers.ModelSerializer):
    changed_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = TicketHistory
        fields = [
            "id",
            "field_name",
            "old_value",
            "new_value",
            "changed_by",
            "created_at",
        ]


class TicketSerializer(serializers.ModelSerializer):
    category = TicketCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=TicketCategory.objects.filter(is_active=True),
        source="category",
        write_only=True,
    )

    reporter = UserSummarySerializer(read_only=True)
    assignee = UserSummarySerializer(read_only=True)

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(
            role=User.Role.IT_ENGINEER,
        ),
        source="assignee",
        write_only=True,
        required=False,
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_no",
            "title",
            "description",
            "resolution_note",
            "category",
            "category_id",
            "reporter",
            "assignee",
            "assignee_id",
            "priority",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "ticket_no",
            "reporter",
            "assignee",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context.get("request")

        return create_ticket(
            validated_data=validated_data,
            reporter=request.user,
        )

    def validate(self, attrs):
        request = self.context.get("request")

        if not request:
            return attrs

        if self.instance is None:
            return validate_ticket_create(
                validated_data=attrs,
                user=request.user,
            )

        return validate_ticket_update(
            ticket=self.instance,
            validated_data=attrs,
            user=request.user,
        )

    def update(self, instance, validated_data):
        request = self.context.get("request")

        changed_by = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        return update_ticket_with_history(
            ticket=instance,
            validated_data=validated_data,
            changed_by=changed_by,
        )
