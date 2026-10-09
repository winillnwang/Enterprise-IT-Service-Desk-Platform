import pytest

from rest_framework.test import APIClient

from accounts.models import (
    Department,
    User,
)
from tickets.models import TicketCategory


@pytest.mark.django_db
def test_employee_cannot_access_system_user_api():
    employee = User.objects.create_user(
        username="system_employee_denied",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    client = APIClient()
    client.force_authenticate(
        user=employee
    )

    response = client.get(
        "/api/admin/users/"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_it_engineer_cannot_access_system_user_api():
    engineer = User.objects.create_user(
        username="system_engineer_denied",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    client = APIClient()
    client.force_authenticate(
        user=engineer
    )

    response = client.get(
        "/api/admin/users/"
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_it_manager_can_access_system_user_api():
    manager = User.objects.create_user(
        username="system_manager_allowed",
        password="test1234",
        role=User.Role.IT_MANAGER,
    )

    client = APIClient()
    client.force_authenticate(
        user=manager
    )

    response = client.get(
        "/api/admin/users/"
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_can_access_system_user_api():
    admin_user = User.objects.create_user(
        username="system_admin_allowed",
        password="test1234",
        role=User.Role.ADMIN,
    )

    client = APIClient()
    client.force_authenticate(
        user=admin_user
    )

    response = client.get(
        "/api/admin/users/"
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_it_manager_can_create_user():
    manager = User.objects.create_user(
        username="system_manager_create",
        password="test1234",
        role=User.Role.IT_MANAGER,
    )

    department = Department.objects.create(
        code="SYSIT",
        name="System IT",
        description="System management test",
    )

    client = APIClient()
    client.force_authenticate(
        user=manager
    )

    response = client.post(
        "/api/admin/users/",
        {
            "username":
                "system_created_user",

            "email":
                "created@example.com",

            "first_name":
                "Created",

            "last_name":
                "User",

            "role":
                User.Role.IT_ENGINEER,

            "department_id":
                department.id,

            "is_active":
                True,

            "password":
                "secure1234",
        },
        format="json",
    )

    assert response.status_code == 201

    created_user = User.objects.get(
        username="system_created_user"
    )

    assert (
        created_user.role
        == User.Role.IT_ENGINEER
    )

    assert (
        created_user.department
        == department
    )

    assert created_user.is_active is True

    assert created_user.check_password(
        "secure1234"
    )


@pytest.mark.django_db
def test_it_manager_can_update_user():
    manager = User.objects.create_user(
        username="system_manager_update",
        password="test1234",
        role=User.Role.IT_MANAGER,
    )

    department = Department.objects.create(
        code="SYSHR",
        name="System HR",
        description="System update test",
    )

    target_user = User.objects.create_user(
        username="system_target_user",
        password="test1234",
        role=User.Role.EMPLOYEE,
        is_active=True,
    )

    client = APIClient()
    client.force_authenticate(
        user=manager
    )

    response = client.patch(
        (
            f"/api/admin/users/"
            f"{target_user.id}/"
        ),
        {
            "role":
                User.Role.IT_ENGINEER,

            "department_id":
                department.id,

            "is_active":
                False,
        },
        format="json",
    )

    assert response.status_code == 200

    target_user.refresh_from_db()

    assert (
        target_user.role
        == User.Role.IT_ENGINEER
    )

    assert (
        target_user.department
        == department
    )

    assert target_user.is_active is False


@pytest.mark.django_db
def test_it_manager_can_create_and_update_department():
    manager = User.objects.create_user(
        username="system_manager_department",
        password="test1234",
        role=User.Role.IT_MANAGER,
    )

    client = APIClient()
    client.force_authenticate(
        user=manager
    )

    create_response = client.post(
        "/api/admin/departments/",
        {
            "code":
                "FIN",

            "name":
                "財務部",

            "description":
                "財務部門",
        },
        format="json",
    )

    assert create_response.status_code == 201

    department_id = (
        create_response.data["id"]
    )

    update_response = client.patch(
        (
            f"/api/admin/departments/"
            f"{department_id}/"
        ),
        {
            "name":
                "財務管理部",

            "description":
                "更新後的部門說明",
        },
        format="json",
    )

    assert update_response.status_code == 200

    department = Department.objects.get(
        id=department_id
    )

    assert (
        department.name
        == "財務管理部"
    )

    assert (
        department.description
        == "更新後的部門說明"
    )


@pytest.mark.django_db
def test_it_manager_can_create_and_update_ticket_category():
    manager = User.objects.create_user(
        username="system_manager_category",
        password="test1234",
        role=User.Role.IT_MANAGER,
    )

    client = APIClient()
    client.force_authenticate(
        user=manager
    )

    create_response = client.post(
        "/api/admin/ticket-categories/",
        {
            "code":
                "SEC",

            "name":
                "資訊安全",

            "description":
                "資訊安全相關問題",

            "is_active":
                True,
        },
        format="json",
    )

    assert create_response.status_code == 201

    category_id = (
        create_response.data["id"]
    )

    update_response = client.patch(
        (
            "/api/admin/"
            "ticket-categories/"
            f"{category_id}/"
        ),
        {
            "name":
                "資訊安全事件",

            "is_active":
                False,
        },
        format="json",
    )

    assert update_response.status_code == 200

    category = TicketCategory.objects.get(
        id=category_id
    )

    assert (
        category.name
        == "資訊安全事件"
    )

    assert category.is_active is False