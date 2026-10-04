from rest_framework import serializers

from accounts.models import User
from .models import Ticket, TicketCategory


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


class TicketSerializer(serializers.ModelSerializer):
    category = TicketCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=TicketCategory.objects.filter(is_active=True),
        source="category",
        write_only=True,
    )

    reporter = UserSummarySerializer(read_only=True)
    assignee = UserSummarySerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_no",
            "title",
            "description",
            "category",
            "category_id",
            "reporter",
            "assignee",
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

    def validate(self, attrs):
        request = self.context.get("request")

        if not request:
            return attrs

        user = request.user

        # Employee 不能修改 priority
        if (
            user.role == "employee"
            and self.instance is not None
            and "priority" in attrs
        ):
            raise serializers.ValidationError(
                {
                    "priority": "Employee users cannot change ticket priority."
                }
            )

        # Employee 不能修改 status
        if (
            user.role == "employee"
            and self.instance is not None
            and "status" in attrs
        ):
            raise serializers.ValidationError(
                {
                    "status": "Employee users cannot change ticket status."
                }
            )

        # Ticket status transition 驗證
        if self.instance is not None and "status" in attrs:
            current_status = self.instance.status
            new_status = attrs["status"]

            allowed_transitions = {
                Ticket.Status.OPEN: [
                    Ticket.Status.ASSIGNED,
                ],
                Ticket.Status.ASSIGNED: [
                    Ticket.Status.IN_PROGRESS,
                ],
                Ticket.Status.IN_PROGRESS: [
                    Ticket.Status.RESOLVED,
                ],
                Ticket.Status.RESOLVED: [
                    Ticket.Status.CLOSED,
                ],
                Ticket.Status.CLOSED: [],
            }

            if new_status not in allowed_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    {
                        "status": (
                            f"Invalid status transition: "
                            f"{current_status} -> {new_status}"
                        )
                    }
                )

        return attrs
