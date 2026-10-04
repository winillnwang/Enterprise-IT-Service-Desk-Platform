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

    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(
            role__in=[
                User.Role.IT_ENGINEER,
                User.Role.IT_MANAGER,
                User.Role.ADMIN,
            ]
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

        # Employee 不能指定 assignee
        if (
            user.role == "employee"
            and self.instance is not None
            and "assignee" in attrs
        ):
            raise serializers.ValidationError(
                {
                    "assignee_id": (
                        "Employee users cannot assign tickets."
                    )
                }
            )

        # 指派工單時必須有 assignee
        if self.instance is not None:
            new_status = attrs.get("status", self.instance.status)
            new_assignee = attrs.get("assignee", self.instance.assignee)

            if new_status == Ticket.Status.ASSIGNED and new_assignee is None:
                raise serializers.ValidationError(
                    {"assignee_id": ("An assignee is required when assigning a ticket.")}
                )

            if new_status == Ticket.Status.IN_PROGRESS and new_assignee is None:
                raise serializers.ValidationError(
                    {"assignee_id": ("An assignee is required before starting work.")}
                )

        # Ticket status transition 驗證
        if self.instance is not None and "status" in attrs:
            current_status = self.instance.status
            new_status = attrs["status"]

                # 只有被指派的工程師才能開始處理工單
            if (
                new_status == Ticket.Status.IN_PROGRESS
                and self.instance.assignee != user
                and user.role not in ["it_manager", "admin"]
            ):
                raise serializers.ValidationError(
                    {
                        "status": (
                            "Only the assigned engineer can start working on this ticket."
                        )
                    }
                )

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
