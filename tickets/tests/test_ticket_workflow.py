import pytest
from rest_framework.exceptions import ValidationError

from accounts.models import User
from tickets.models import (
    Ticket,
    TicketCategory,
    TicketHistory,
)
from tickets.services import (
    update_ticket_with_history,
    validate_ticket_update,
)

@pytest.mark.django_db
def test_employee_cannot_change_ticket_status():
    employee = User.objects.create_user(
        username="employee_test",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    category = TicketCategory.objects.create(
        code="TEST",
        name="測試分類",
    )

    ticket = Ticket.objects.create(
        title="測試工單",
        description="測試 Employee 權限",
        category=category,
        reporter=employee,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.OPEN,
    )

    with pytest.raises(ValidationError) as exc_info:
        validate_ticket_update(
            ticket=ticket,
            validated_data={
                "status": Ticket.Status.CLOSED,
            },
            user=employee,
        )

    assert "Employee users cannot change ticket status." in str(exc_info.value)


@pytest.mark.django_db
def test_assigned_engineer_can_start_work():
    engineer = User.objects.create_user(
        username="engineer_test",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    category = TicketCategory.objects.create(
        code="TEST2",
        name="測試分類 2",
    )

    ticket = Ticket.objects.create(
        title="工程師測試工單",
        description="測試合法 Workflow",
        category=category,
        reporter=engineer,
        assignee=engineer,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.ASSIGNED,
    )

    validated_data = {
        "status": Ticket.Status.IN_PROGRESS,
    }

    result = validate_ticket_update(
        ticket=ticket,
        validated_data=validated_data,
        user=engineer,
    )

    assert result == validated_data


@pytest.mark.django_db
def test_open_ticket_cannot_jump_directly_to_closed():
    engineer = User.objects.create_user(
        username="engineer_invalid_transition",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    category = TicketCategory.objects.create(
        code="TEST3",
        name="測試分類 3",
    )

    ticket = Ticket.objects.create(
        title="非法 Workflow 測試",
        description="測試 open 不能直接 closed",
        category=category,
        reporter=engineer,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.OPEN,
    )

    with pytest.raises(ValidationError) as exc_info:
        validate_ticket_update(
            ticket=ticket,
            validated_data={
                "status": Ticket.Status.CLOSED,
            },
            user=engineer,
        )

    assert "Invalid status transition: open -> closed" in str(exc_info.value)


@pytest.mark.django_db
def test_update_ticket_creates_history_record():
    engineer = User.objects.create_user(
        username="engineer_history_test",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    category = TicketCategory.objects.create(
        code="TEST4",
        name="測試分類 4",
    )

    ticket = Ticket.objects.create(
        title="History 測試",
        description="測試更新時建立歷程",
        category=category,
        reporter=engineer,
        assignee=engineer,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.ASSIGNED,
    )

    update_ticket_with_history(
        ticket=ticket,
        validated_data={
            "status": Ticket.Status.IN_PROGRESS,
        },
        changed_by=engineer,
    )

    history = TicketHistory.objects.get(
        ticket=ticket,
        field_name="status",
    )

    assert history.old_value == Ticket.Status.ASSIGNED
    assert history.new_value == Ticket.Status.IN_PROGRESS
    assert history.changed_by == engineer


@pytest.mark.django_db
def test_update_multiple_fields_creates_multiple_history_records():
    engineer1 = User.objects.create_user(
        username="engineer_multi_1",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    engineer2 = User.objects.create_user(
        username="engineer_multi_2",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    category = TicketCategory.objects.create(
        code="TEST5",
        name="測試分類 5",
    )

    ticket = Ticket.objects.create(
        title="多欄位 History 測試",
        description="測試一次修改兩個欄位",
        category=category,
        reporter=engineer1,
        assignee=engineer1,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.OPEN,
    )

    update_ticket_with_history(
        ticket=ticket,
        validated_data={
            "status": Ticket.Status.ASSIGNED,
            "assignee": engineer2,
        },
        changed_by=engineer1,
    )

    histories = TicketHistory.objects.filter(ticket=ticket)

    assert histories.count() == 2

    assert histories.filter(
        field_name="status",
        old_value=Ticket.Status.OPEN,
        new_value=Ticket.Status.ASSIGNED,
    ).exists()

    assert histories.filter(
        field_name="assignee",
        old_value=engineer1.username,
        new_value=engineer2.username,
    ).exists()


@pytest.mark.django_db
def test_unassigned_engineer_cannot_start_work():
    assigned_engineer = User.objects.create_user(
        username="assigned_engineer_test",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    other_engineer = User.objects.create_user(
        username="other_engineer_test",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    category = TicketCategory.objects.create(
        code="TEST6",
        name="測試分類 6",
    )

    ticket = Ticket.objects.create(
        title="未指派工程師測試",
        description="測試只有 assignee 可以開始處理",
        category=category,
        reporter=assigned_engineer,
        assignee=assigned_engineer,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.ASSIGNED,
    )

    with pytest.raises(ValidationError) as exc_info:
        validate_ticket_update(
            ticket=ticket,
            validated_data={
                "status": Ticket.Status.IN_PROGRESS,
            },
            user=other_engineer,
        )

    assert "Only the assigned engineer can start working on this ticket." in str(
        exc_info.value
    )


@pytest.mark.django_db
def test_employee_cannot_modify_resolution_note():
    employee = User.objects.create_user(
        username="employee_resolution_test",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    category = TicketCategory.objects.create(
        code="TEST_RESOLUTION",
        name="處理內容測試",
    )

    ticket = Ticket.objects.create(
        title="處理內容權限測試",
        description="Employee 不應該能寫 resolution_note",
        category=category,
        reporter=employee,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.OPEN,
    )

    with pytest.raises(ValidationError) as exc_info:
        validate_ticket_update(
            ticket=ticket,
            validated_data={
                "resolution_note": "我自己填處理結果",
            },
            user=employee,
        )

    assert "Employee users cannot modify resolution notes." in str(exc_info.value)


@pytest.mark.django_db
def test_ticket_cannot_be_resolved_without_resolution_note():
    engineer = User.objects.create_user(
        username="engineer_resolution_required",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    category = TicketCategory.objects.create(
        code="TEST_RES_REQUIRED",
        name="解決內容必填測試",
    )

    ticket = Ticket.objects.create(
        title="解決內容必填",
        description="測試 resolved 前必須填處理內容",
        category=category,
        reporter=engineer,
        assignee=engineer,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.IN_PROGRESS,
        resolution_note="",
    )

    with pytest.raises(ValidationError) as exc_info:
        validate_ticket_update(
            ticket=ticket,
            validated_data={
                "status": Ticket.Status.RESOLVED,
            },
            user=engineer,
        )

    assert "A resolution note is required before resolving a ticket." in str(
        exc_info.value
    )


@pytest.mark.django_db
def test_ticket_can_be_resolved_with_resolution_note():
    engineer = User.objects.create_user(
        username="engineer_resolution_success",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    category = TicketCategory.objects.create(
        code="TEST_RES_SUCCESS",
        name="解決成功測試",
    )

    ticket = Ticket.objects.create(
        title="解決成功測試",
        description="測試有處理內容時可以 resolved",
        category=category,
        reporter=engineer,
        assignee=engineer,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.IN_PROGRESS,
        resolution_note="已完成故障排除並確認恢復正常。",
    )

    validated_data = {
        "status": Ticket.Status.RESOLVED,
    }

    result = validate_ticket_update(
        ticket=ticket,
        validated_data=validated_data,
        user=engineer,
    )

    assert result == validated_data


@pytest.mark.django_db
def test_resolved_ticket_can_be_closed():
    engineer = User.objects.create_user(
        username="engineer_close_success",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    category = TicketCategory.objects.create(
        code="TEST_CLOSE_SUCCESS",
        name="關閉成功測試",
    )

    ticket = Ticket.objects.create(
        title="關閉工單測試",
        description="測試 resolved 可以進入 closed",
        category=category,
        reporter=engineer,
        assignee=engineer,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.RESOLVED,
        resolution_note="問題已排除並確認使用者恢復正常使用。",
    )

    validated_data = {
        "status": Ticket.Status.CLOSED,
    }

    result = validate_ticket_update(
        ticket=ticket,
        validated_data=validated_data,
        user=engineer,
    )

    assert result == validated_data


@pytest.mark.django_db
def test_it_engineer_cannot_assign_ticket():
    engineer = User.objects.create_user(
        username="engineer_assign_denied",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    target_engineer = User.objects.create_user(
        username="target_engineer",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    category = TicketCategory.objects.create(
        code="TEST_MANAGER_ASSIGN_1",
        name="主管指派測試 1",
    )

    ticket = Ticket.objects.create(
        title="工程師不可自行指派",
        description="測試 IT Engineer 不可修改 assignee",
        category=category,
        reporter=engineer,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.OPEN,
    )

    with pytest.raises(ValidationError) as exc_info:
        validate_ticket_update(
            ticket=ticket,
            validated_data={
                "assignee": target_engineer,
            },
            user=engineer,
        )

    assert "Only IT Manager can assign or reassign tickets." in str(exc_info.value)


@pytest.mark.django_db
def test_it_manager_can_assign_ticket():
    manager = User.objects.create_user(
        username="manager_assign_success",
        password="test1234",
        role=User.Role.IT_MANAGER,
    )

    engineer = User.objects.create_user(
        username="engineer_assign_target",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    category = TicketCategory.objects.create(
        code="TEST_MANAGER_ASSIGN_2",
        name="主管指派測試 2",
    )

    ticket = Ticket.objects.create(
        title="主管可以指派",
        description="測試 IT Manager 可以修改 assignee",
        category=category,
        reporter=manager,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.OPEN,
    )

    validated_data = {
        "assignee": engineer,
    }

    result = validate_ticket_update(
        ticket=ticket,
        validated_data=validated_data,
        user=manager,
    )

    assert result == validated_data


@pytest.mark.django_db
def test_resolved_ticket_cannot_remove_assignee():
    manager = User.objects.create_user(
        username="manager_remove_assignee",
        password="test1234",
        role=User.Role.IT_MANAGER,
    )

    engineer = User.objects.create_user(
        username="engineer_resolved_ticket",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    category = TicketCategory.objects.create(
        code="ASSIGNEE_REQUIRED",
        name="處理人必填測試",
    )

    ticket = Ticket.objects.create(
        title="已解決工單",
        description="測試取消處理人",
        category=category,
        reporter=manager,
        assignee=engineer,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.RESOLVED,
        resolution_note="問題已處理完成",
    )

    with pytest.raises(ValidationError):
        validate_ticket_update(
            ticket=ticket,
            validated_data={
                "assignee": None,
            },
            user=manager,
        )
