import pytest

from rest_framework.test import APIClient

from accounts.models import (
    Department,
    User,
)
from assets.models import Asset


@pytest.mark.django_db
def test_employee_only_sees_own_assets():
    employee01 = User.objects.create_user(
        username="employee_asset_01",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    employee02 = User.objects.create_user(
        username="employee_asset_02",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    own_asset = Asset.objects.create(
        asset_no="AST-TEST-001",
        name="Own Laptop",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.IN_USE,
        assigned_to=employee01,
    )

    Asset.objects.create(
        asset_no="AST-TEST-002",
        name="Other Laptop",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.IN_USE,
        assigned_to=employee02,
    )

    client = APIClient()
    client.force_authenticate(user=employee01)

    response = client.get("/api/assets/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == own_asset.id


@pytest.mark.django_db
def test_employee_cannot_create_asset():
    employee = User.objects.create_user(
        username="employee_asset_create",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    client = APIClient()
    client.force_authenticate(user=employee)

    response = client.post(
        "/api/assets/",
        {
            "asset_no": "AST-TEST-003",
            "name": "Illegal Asset",
            "asset_type": "laptop",
            "status": "available",
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_employee_cannot_update_asset():
    employee = User.objects.create_user(
        username="employee_asset_update",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    asset = Asset.objects.create(
        asset_no="AST-TEST-004",
        name="Employee Laptop",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.IN_USE,
        assigned_to=employee,
    )

    client = APIClient()
    client.force_authenticate(user=employee)

    response = client.patch(
        f"/api/assets/{asset.id}/",
        {
            "status": "retired",
        },
        format="json",
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_it_staff_can_see_all_assets():
    engineer = User.objects.create_user(
        username="engineer_asset_list",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    employee = User.objects.create_user(
        username="employee_asset_owner",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    Asset.objects.create(
        asset_no="AST-TEST-005",
        name="Asset One",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.AVAILABLE,
    )

    Asset.objects.create(
        asset_no="AST-TEST-006",
        name="Asset Two",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.IN_USE,
        assigned_to=employee,
    )

    client = APIClient()
    client.force_authenticate(user=engineer)

    response = client.get("/api/assets/")

    assert response.status_code == 200
    assert len(response.data) == 2


@pytest.mark.django_db
def test_assigning_user_sets_asset_to_in_use():
    engineer = User.objects.create_user(
        username="engineer_asset_assign",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    employee = User.objects.create_user(
        username="employee_asset_assign",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    asset = Asset.objects.create(
        asset_no="AST-TEST-007",
        name="Available Laptop",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.AVAILABLE,
    )

    client = APIClient()
    client.force_authenticate(user=engineer)

    response = client.patch(
        f"/api/assets/{asset.id}/",
        {
            "assigned_to_id": employee.id,
        },
        format="json",
    )

    assert response.status_code == 200

    asset.refresh_from_db()

    assert asset.assigned_to == employee
    assert asset.status == Asset.Status.IN_USE


@pytest.mark.django_db
def test_removing_user_sets_asset_to_available():
    engineer = User.objects.create_user(
        username="engineer_asset_unassign",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    employee = User.objects.create_user(
        username="employee_asset_unassign",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    asset = Asset.objects.create(
        asset_no="AST-TEST-008",
        name="Assigned Laptop",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.IN_USE,
        assigned_to=employee,
    )

    client = APIClient()
    client.force_authenticate(user=engineer)

    response = client.patch(
        f"/api/assets/{asset.id}/",
        {
            "assigned_to_id": None,
        },
        format="json",
    )

    assert response.status_code == 200

    asset.refresh_from_db()

    assert asset.assigned_to is None
    assert asset.status == Asset.Status.AVAILABLE


@pytest.mark.django_db
def test_in_use_asset_requires_assigned_user():
    engineer = User.objects.create_user(
        username="engineer_asset_invalid",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    asset = Asset.objects.create(
        asset_no="AST-TEST-009",
        name="Invalid Test Laptop",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.AVAILABLE,
    )

    client = APIClient()
    client.force_authenticate(user=engineer)

    response = client.patch(
        f"/api/assets/{asset.id}/",
        {
            "status": "in_use",
            "assigned_to_id": None,
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_create_asset_with_assignee_sets_status_to_in_use():
    engineer = User.objects.create_user(
        username="engineer_asset_create_assign",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    employee = User.objects.create_user(
        username="employee_asset_create_assign",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    client = APIClient()

    client.force_authenticate(user=engineer)

    response = client.post(
        "/api/assets/",
        {
            "asset_no": "AST-TEST-010",
            "name": "Assigned New Laptop",
            "asset_type": "laptop",
            "status": "available",
            "assigned_to_id": employee.id,
        },
        format="json",
    )

    assert response.status_code == 201

    asset = Asset.objects.get(asset_no="AST-TEST-010")

    assert asset.assigned_to == employee
    assert asset.status == Asset.Status.IN_USE


@pytest.mark.django_db
def test_it_staff_can_update_asset_department():
    engineer = User.objects.create_user(
        username="engineer_asset_department",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    department = Department.objects.create(
        code="IT-TEST",
        name="Test IT Department",
    )

    asset = Asset.objects.create(
        asset_no="AST-TEST-011",
        name="Department Test Laptop",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.AVAILABLE,
    )

    client = APIClient()
    client.force_authenticate(user=engineer)

    response = client.patch(
        f"/api/assets/{asset.id}/",
        {
            "department_id": department.id,
        },
        format="json",
    )

    assert response.status_code == 200

    asset.refresh_from_db()

    assert asset.department == department


@pytest.mark.django_db
def test_asset_list_can_filter_by_search():
    engineer = User.objects.create_user(
        username="engineer_asset_search",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    Asset.objects.create(
        asset_no="AST-SEARCH-001",
        name="Dell Latitude 5450",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.AVAILABLE,
    )

    Asset.objects.create(
        asset_no="AST-SEARCH-002",
        name="Lenovo ThinkPad T14",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.AVAILABLE,
    )

    client = APIClient()
    client.force_authenticate(user=engineer)

    response = client.get("/api/assets/?search=Dell")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["asset_no"] == "AST-SEARCH-001"


@pytest.mark.django_db
def test_asset_list_can_filter_by_status():
    engineer = User.objects.create_user(
        username="engineer_asset_status_filter",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    employee = User.objects.create_user(
        username="employee_asset_status_filter",
        password="test1234",
        role=User.Role.EMPLOYEE,
    )

    Asset.objects.create(
        asset_no="AST-STATUS-001",
        name="Available Laptop",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.AVAILABLE,
    )

    Asset.objects.create(
        asset_no="AST-STATUS-002",
        name="Assigned Laptop",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.IN_USE,
        assigned_to=employee,
    )

    client = APIClient()
    client.force_authenticate(user=engineer)

    response = client.get("/api/assets/?status=in_use")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["asset_no"] == "AST-STATUS-002"


@pytest.mark.django_db
def test_asset_list_can_filter_by_asset_type():
    engineer = User.objects.create_user(
        username="engineer_asset_type_filter",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    Asset.objects.create(
        asset_no="AST-TYPE-001",
        name="Test Laptop",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.AVAILABLE,
    )

    Asset.objects.create(
        asset_no="AST-TYPE-002",
        name="Test Monitor",
        asset_type=Asset.AssetType.MONITOR,
        status=Asset.Status.AVAILABLE,
    )

    client = APIClient()
    client.force_authenticate(user=engineer)

    response = client.get("/api/assets/?asset_type=monitor")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["asset_no"] == "AST-TYPE-002"


@pytest.mark.django_db
def test_asset_list_can_filter_by_department():
    engineer = User.objects.create_user(
        username="engineer_asset_department_filter",
        password="test1234",
        role=User.Role.IT_ENGINEER,
    )

    department_it = Department.objects.create(
        code="IT-FILTER",
        name="IT Filter Department",
    )

    department_hr = Department.objects.create(
        code="HR-FILTER",
        name="HR Filter Department",
    )

    Asset.objects.create(
        asset_no="AST-DEPT-001",
        name="IT Laptop",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.AVAILABLE,
        department=department_it,
    )

    Asset.objects.create(
        asset_no="AST-DEPT-002",
        name="HR Laptop",
        asset_type=Asset.AssetType.LAPTOP,
        status=Asset.Status.AVAILABLE,
        department=department_hr,
    )

    client = APIClient()
    client.force_authenticate(user=engineer)

    response = client.get(f"/api/assets/?department={department_it.id}")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["asset_no"] == "AST-DEPT-001"
