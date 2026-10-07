import logging

from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import Ticket, TicketHistory

logger = logging.getLogger(__name__)


def validate_ticket_create(
    *,
    validated_data,
    user,
):
    # Employee 建立工單時不可直接指定狀態
    if user.role == "employee" and "status" in validated_data:
        raise ValidationError({"status": "Employee users cannot set ticket status."})

    # Employee 建立工單時不可指定處理人
    if user.role == "employee" and "assignee" in validated_data:
        raise ValidationError({"assignee_id": "Employee users cannot assign tickets."})

    return validated_data


def validate_ticket_update(
    *,
    ticket,
    validated_data,
    user,
):
    # Employee 不可修改優先級
    if user.role == "employee" and "priority" in validated_data:
        raise ValidationError(
            {"priority": "Employee users cannot change ticket priority."}
        )

    # Employee 不可修改狀態
    if user.role == "employee" and "status" in validated_data:
        raise ValidationError({"status": "Employee users cannot change ticket status."})

    # Employee 不可修改處理內容
    if user.role == "employee" and "resolution_note" in validated_data:
        raise ValidationError(
            {"resolution_note": "Employee users cannot modify resolution notes."}
        )

    # 只有 IT Manager 可以指派或重新指派工單
    if "assignee" in validated_data and user.role != "it_manager":
        raise ValidationError(
            {"assignee_id": "Only IT Manager can assign or reassign tickets."}
        )

    # Open 工單被指派處理人時，
    # 如果沒有另外指定 status，
    # 自動轉為 Assigned
    if (
        ticket.status == Ticket.Status.OPEN
        and "assignee" in validated_data
        and validated_data["assignee"] is not None
        and "status" not in validated_data
    ):
        validated_data["status"] = Ticket.Status.ASSIGNED

    # 計算更新後的最終狀態
    new_status = validated_data.get(
        "status",
        ticket.status,
    )

    new_assignee = validated_data.get(
        "assignee",
        ticket.assignee,
    )

    new_resolution_note = validated_data.get(
        "resolution_note",
        ticket.resolution_note,
    )

    # Assigned 必須有處理人
    if new_status == Ticket.Status.ASSIGNED and new_assignee is None:
        raise ValidationError(
            {"assignee_id": "An assignee is required when assigning a ticket."}
        )

    # In Progress 必須有處理人
    if new_status == Ticket.Status.IN_PROGRESS and new_assignee is None:
        raise ValidationError(
            {"assignee_id": "An assignee is required before starting work."}
        )

    # Resolved 必須有處理內容
    if new_status == Ticket.Status.RESOLVED and not new_resolution_note.strip():
        raise ValidationError(
            {
                "resolution_note": "A resolution note is required before resolving a ticket."
            }
        )

    current_status = ticket.status

    # 只有真的有修改 status 時，
    # 才檢查 Workflow transition
    if "status" in validated_data:

        # 狀態沒有改變時，不需要檢查 transition
        if new_status != current_status:

            # 只有被指派的工程師可以開始處理
            # IT Manager / Admin 可以 override
            if (
                new_status == Ticket.Status.IN_PROGRESS
                and ticket.assignee != user
                and user.role
                not in [
                    "it_manager",
                    "admin",
                ]
            ):
                raise ValidationError(
                    {
                        "status": "Only the assigned engineer can "
                        "start working on this ticket."
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

            if new_status not in allowed_transitions.get(
                current_status,
                [],
            ):
                raise ValidationError(
                    {
                        "status": f"Invalid status transition: "
                        f"{current_status} -> "
                        f"{new_status}"
                    }
                )

    # Resolved / Closed 工單
    # 不可以沒有處理人
    if (
        new_status
        in [
            Ticket.Status.RESOLVED,
            Ticket.Status.CLOSED,
        ]
        and new_assignee is None
    ):
        raise ValidationError(
            {"assignee_id": "Resolved or closed tickets " "must have an assignee."}
        )

    return validated_data


def create_ticket(
    *,
    validated_data,
    reporter,
):
    ticket = Ticket.objects.create(
        reporter=reporter,
        **validated_data,
    )

    logger.info(
        "Ticket created: ticket_no=%s reporter=%s",
        ticket.ticket_no,
        reporter.username,
    )

    return ticket


@transaction.atomic
def update_ticket_with_history(
    *,
    ticket,
    validated_data,
    changed_by,
):
    old_status = ticket.status
    old_priority = ticket.priority
    old_assignee = ticket.assignee
    old_resolution_note = ticket.resolution_note

    for field, value in validated_data.items():
        setattr(
            ticket,
            field,
            value,
        )

    ticket.save()

    # Status History
    if old_status != ticket.status:
        TicketHistory.objects.create(
            ticket=ticket,
            changed_by=changed_by,
            field_name="status",
            old_value=old_status or "",
            new_value=ticket.status or "",
        )

    # Priority History
    if old_priority != ticket.priority:
        TicketHistory.objects.create(
            ticket=ticket,
            changed_by=changed_by,
            field_name="priority",
            old_value=old_priority or "",
            new_value=ticket.priority or "",
        )

    # Assignee History
    if old_assignee != ticket.assignee:
        TicketHistory.objects.create(
            ticket=ticket,
            changed_by=changed_by,
            field_name="assignee",
            old_value=(old_assignee.username if old_assignee else ""),
            new_value=(ticket.assignee.username if ticket.assignee else ""),
        )

    # Resolution Note History
    if old_resolution_note != ticket.resolution_note:
        TicketHistory.objects.create(
            ticket=ticket,
            changed_by=changed_by,
            field_name="resolution_note",
            old_value=old_resolution_note or "",
            new_value=ticket.resolution_note or "",
        )

    logger.info(
        "Ticket updated: ticket_no=%s changed_by=%s",
        ticket.ticket_no,
        (changed_by.username if changed_by else "system"),
    )

    return ticket
