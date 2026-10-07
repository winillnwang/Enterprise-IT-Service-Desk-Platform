import pytest
from rest_framework.test import APIClient

from accounts.models import User
from tickets.models import (
    Ticket,
    TicketCategory,
    TicketHistory,
)

@pytest.mark.django_db
def test_create_ticket_uses_authenticated_user_as_reporter():
    user = User.objects.create_user(
        username="employee_api_test",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    fake_user = User.objects.create_user(
        username="fake_reporter",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    category = TicketCategory.objects.create(
        code="API_TEST",
        name="API 測試分類",
    )

    client = APIClient()

    client.force_authenticate(user=user)

    response = client.post(
        "/api/tickets/",
        {
            "title": "API 建立工單測試",
            "description": "測試 reporter 是否可以被偽造",
            "category_id": category.id,
            "priority": Ticket.Priority.MEDIUM,
            # 故意偽造 Reporter
            "reporter": fake_user.id,
        },
        format="json",
    )

    assert response.status_code == 201

    ticket = Ticket.objects.get(id=response.data["id"])

    assert ticket.reporter == user

    assert ticket.reporter != fake_user

    assert response.data["reporter"]["username"] == ("employee_api_test")


@pytest.mark.django_db
def test_employee_cannot_create_ticket_with_privileged_fields():
    employee = User.objects.create_user(
        username="employee_privilege_test",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    engineer = User.objects.create_user(
        username="engineer_privilege_test",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    category = TicketCategory.objects.create(
        code="API_SEC",
        name="API 權限測試",
    )

    client = APIClient()

    client.force_authenticate(user=employee)

    response = client.post(
        "/api/tickets/",
        {
            "title": "嘗試越權建立工單",
            "description": "Employee 嘗試直接建立已關閉工單",
            "category_id": category.id,
            "priority": Ticket.Priority.MEDIUM,
            # Employee 不應該能控制這兩個欄位
            "status": Ticket.Status.CLOSED,
            "assignee_id": engineer.id,
        },
        format="json",
    )

    assert response.status_code == 400

    assert Ticket.objects.filter(title="嘗試越權建立工單").exists() is False


@pytest.mark.django_db
def test_employee_cannot_access_another_users_ticket():
    employee1 = User.objects.create_user(
        username="employee_owner",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    employee2 = User.objects.create_user(
        username="employee_other",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    category = TicketCategory.objects.create(
        code="API_PERM",
        name="API 權限測試分類",
    )

    ticket = Ticket.objects.create(
        title="私人測試工單",
        description="測試 Employee object permission",
        category=category,
        reporter=employee1,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.OPEN,
    )

    client = APIClient()

    client.force_authenticate(user=employee2)

    response = client.get(f"/api/tickets/{ticket.id}/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_employee_ticket_list_only_contains_own_tickets():
    employee1 = User.objects.create_user(
        username="employee_list_owner",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    employee2 = User.objects.create_user(
        username="employee_list_other",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    category = TicketCategory.objects.create(
        code="API_LIST",
        name="API 列表權限測試",
    )

    own_ticket = Ticket.objects.create(
        title="自己的工單",
        description="Employee 應該看得到",
        category=category,
        reporter=employee1,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.OPEN,
    )

    other_ticket = Ticket.objects.create(
        title="別人的工單",
        description="Employee 不應該看得到",
        category=category,
        reporter=employee2,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.OPEN,
    )

    client = APIClient()

    client.force_authenticate(user=employee1)

    response = client.get("/api/tickets/")

    assert response.status_code == 200

    returned_ids = [ticket["id"] for ticket in response.data]

    assert own_ticket.id in returned_ids
    assert other_ticket.id not in returned_ids


@pytest.mark.django_db
def test_it_engineer_ticket_list_contains_all_tickets():
    employee1 = User.objects.create_user(
        username="employee_all_1",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    employee2 = User.objects.create_user(
        username="employee_all_2",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    engineer = User.objects.create_user(
        username="engineer_all",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    category = TicketCategory.objects.create(
        code="API_ALL",
        name="API 全部工單測試",
    )

    ticket1 = Ticket.objects.create(
        title="工單一",
        description="第一張工單",
        category=category,
        reporter=employee1,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.OPEN,
    )

    ticket2 = Ticket.objects.create(
        title="工單二",
        description="第二張工單",
        category=category,
        reporter=employee2,
        priority=Ticket.Priority.HIGH,
        status=Ticket.Status.OPEN,
    )

    client = APIClient()

    client.force_authenticate(user=engineer)

    response = client.get("/api/tickets/")

    assert response.status_code == 200

    returned_ids = [ticket["id"] for ticket in response.data]

    assert ticket1.id in returned_ids
    assert ticket2.id in returned_ids


@pytest.mark.django_db
def test_it_engineer_cannot_assign_ticket_via_api():
    engineer = User.objects.create_user(
        username="engineer_api_assign_denied",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    target_engineer = User.objects.create_user(
        username="engineer_api_target",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    category = TicketCategory.objects.create(
        code="API_ASSIGN_DENIED",
        name="API 指派拒絕測試",
    )

    ticket = Ticket.objects.create(
        title="API 指派權限測試",
        description="IT Engineer 不可指派",
        category=category,
        reporter=engineer,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.OPEN,
    )

    client = APIClient()
    client.force_authenticate(user=engineer)

    response = client.patch(
        f"/api/tickets/{ticket.id}/",
        {
            "assignee_id": target_engineer.id,
        },
        format="json",
    )

    assert response.status_code == 400

    ticket.refresh_from_db()

    assert ticket.assignee is None


@pytest.mark.django_db
def test_it_manager_can_assign_ticket_via_api():
    manager = User.objects.create_user(
        username="manager_api_assign_success",
        password="test1234",
        role=User.Role.IT_MANAGER,
    )

    engineer = User.objects.create_user(
        username="engineer_api_assign_success",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    category = TicketCategory.objects.create(
        code="API_ASSIGN_SUCCESS",
        name="API 指派成功測試",
    )

    ticket = Ticket.objects.create(
        title="主管 API 指派測試",
        description="IT Manager 可以指派",
        category=category,
        reporter=manager,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.OPEN,
    )

    client = APIClient()
    client.force_authenticate(user=manager)

    response = client.patch(
        f"/api/tickets/{ticket.id}/",
        {
            "assignee_id": engineer.id,
        },
        format="json",
    )

    assert response.status_code == 200

    ticket.refresh_from_db()

    assert ticket.assignee == engineer
    assert ticket.status == Ticket.Status.ASSIGNED

    assert TicketHistory.objects.filter(
        ticket=ticket,
        field_name="assignee",
    ).exists()

    assert TicketHistory.objects.filter(
        ticket=ticket,
        field_name="status",
        old_value=Ticket.Status.OPEN,
        new_value=Ticket.Status.ASSIGNED,
    ).exists()


@pytest.mark.django_db
def test_employee_cannot_view_other_users_ticket_history():
    employee01 = User.objects.create_user(
        username="employee_history_01",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    employee02 = User.objects.create_user(
        username="employee_history_02",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    category = TicketCategory.objects.create(
        code="HIST",
        name="History Test",
        is_active=True,
    )

    ticket = Ticket.objects.create(
        title="Other User Ticket",
        description="History permission test",
        category=category,
        reporter=employee02,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.OPEN,
    )

    TicketHistory.objects.create(
        ticket=ticket,
        changed_by=employee02,
        field_name="status",
        old_value="",
        new_value=Ticket.Status.OPEN,
    )

    client = APIClient()
    client.force_authenticate(user=employee01)

    response = client.get(f"/api/tickets/{ticket.id}/history/")

    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_employee_can_view_own_ticket_history():
    employee = User.objects.create_user(
        username="employee_history_owner",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    category = TicketCategory.objects.create(
        code="HIST-OWN",
        name="History Own Test",
        is_active=True,
    )

    ticket = Ticket.objects.create(
        title="Own Ticket",
        description="Own history permission test",
        category=category,
        reporter=employee,
        priority=Ticket.Priority.MEDIUM,
        status=Ticket.Status.OPEN,
    )

    TicketHistory.objects.create(
        ticket=ticket,
        changed_by=employee,
        field_name="status",
        old_value="",
        new_value=Ticket.Status.OPEN,
    )

    client = APIClient()
    client.force_authenticate(user=employee)

    response = client.get(f"/api/tickets/{ticket.id}/history/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["field_name"] == "status"
    assert response.data[0]["new_value"] == Ticket.Status.OPEN
