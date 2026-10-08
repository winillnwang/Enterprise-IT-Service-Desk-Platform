# Enterprise IT Service Desk Platform

企業 IT 維運暨工單管理平台，使用 Django REST Framework 建置的企業級 IT Service Desk 後端系統。

## Project Overview

本專案模擬企業內部 IT Helpdesk / Service Desk 的實際工作流程，提供工單管理、角色權限控制、資產管理、REST API、JWT 驗證與 API 文件等功能。

## Features

- JWT Authentication
- Role-Based Access Control (RBAC)
  - Employee
  - IT Engineer
  - IT Manager
  - Admin
- Ticket Management
  - Create ticket
  - Assign / reassign ticket
  - Ticket status workflow
  - Resolution note
  - Ticket history tracking
- Asset Management
  - Asset list / detail / create
  - Asset assignment
  - Department association
  - Asset status management
- Dashboard Summary
  - Ticket totals
  - Status distribution
  - Priority distribution
- RESTful API
- Swagger / OpenAPI Documentation
- Automated Testing with Pytest
- Docker / Docker Compose
- GitHub Actions CI

## Tech Stack

- Python 3.14
- Django 6.1.1
- Django REST Framework 3.18.1
- MySQL 8.4
- djangorestframework-simplejwt
- drf-spectacular
- Pytest
- Docker
- Docker Compose
- GitHub Actions

## System Roles

### Employee

- Create tickets
- View own tickets
- View own assigned assets
- Cannot assign tickets
- Cannot modify ticket operational status
- Cannot manage assets

### IT Engineer

- View and handle tickets
- Update ticket workflow status
- View dashboard
- View and manage assets

### IT Manager

- Assign / reassign tickets
- Manage ticket workflow
- View dashboard
- Manage assets

### Admin

- Full administrative access
- Manage users and system data
- Access dashboard and operational functions

## Ticket Workflow

```text
open
  ↓
assigned
  ↓
in_progress
  ↓
resolved
  ↓
closed
```

主要流程規則：

- 新建工單預設為 `open`
- 工單由 IT Manager / Admin 指派後進入 `assigned`
- 負責的 IT Engineer 可將工單更新為 `in_progress`
- 工單完成處理時更新為 `resolved`
- `resolved` 工單需要填寫 resolution note
- 最後可將工單關閉為 `closed`
- 工單狀態與重要欄位變更會記錄於 Ticket History

## API Endpoints

### Authentication

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/auth/login/` | Obtain JWT access and refresh tokens |
| POST | `/api/auth/refresh/` | Refresh JWT access token |
| GET | `/api/auth/me/` | Get current authenticated user |

### Tickets

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/ticket-categories/` | List ticket categories |
| GET | `/api/tickets/` | List tickets |
| POST | `/api/tickets/` | Create a ticket |
| GET | `/api/tickets/<id>/` | Retrieve ticket details |
| PATCH | `/api/tickets/<id>/` | Update a ticket |
| GET | `/api/tickets/<id>/history/` | View ticket history |

### Dashboard

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/dashboard/summary/` | Get ticket dashboard statistics |

### Assets

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/assets/` | List accessible assets |
| POST | `/api/assets/` | Create an asset |
| GET | `/api/assets/<id>/` | Retrieve asset details |
| PATCH | `/api/assets/<id>/` | Update an asset |

### Users and Departments

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/users/it-staff/` | List IT staff |
| GET | `/api/users/asset-assignees/` | List available asset assignees |
| GET | `/api/departments/` | List departments |

### API Documentation

| Endpoint | Description |
| --- | --- |
| `/api/docs/` | Swagger UI |
| `/api/schema/` | OpenAPI schema |

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/winillnwang/Enterprise-IT-Service-Desk-Platform.git
cd Enterprise-IT-Service-Desk-Platform
```

### 2. Create a virtual environment

```bash
python -m venv venv2
```

Windows：

```bat
venv2\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env`:

```bat
copy .env.example .env
```

Then update `.env` with your local MySQL configuration:

```text
DB_NAME=enterprise_it_service_desk_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=8888
```

Create the MySQL database before running migrations.

### 5. Run database migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

Application:

```text
http://127.0.0.1:8000/
```

Swagger UI:

```text
http://127.0.0.1:8000/api/docs/
```

### 7. Run tests

```bash
pytest -v
```

## Docker Setup

The application can also be started with Docker Compose.

### 1. Configure environment variables

Make sure `.env` exists:

```bat
copy .env.example .env
```

Update the database credentials in `.env` as needed.

### 2. Build and start the containers

```bash
docker compose up -d --build
```

Docker Compose starts:

- Django application container
- MySQL 8.4 database container
- Persistent MySQL volume

### 3. Run database migrations

```bash
docker compose exec app python manage.py migrate
```

### 4. Verify Django configuration

```bash
docker compose exec app python manage.py check
```

### 5. Run tests inside Docker

```bash
docker compose exec app pytest -v
```

### 6. Access the application

```text
http://127.0.0.1:8000/
```

Swagger UI:

```text
http://127.0.0.1:8000/api/docs/
```

### 7. Stop the containers

```bash
docker compose down
```

## Continuous Integration

GitHub Actions is configured to automatically validate the project on pushes and pull requests to the `master` branch.

The CI pipeline performs the following steps:

1. Checks out the repository
2. Sets up Python 3.14
3. Starts a MySQL 8.4 service
4. Installs system and Python dependencies
5. Runs the Django system check
6. Runs the complete Pytest test suite

Workflow configuration:

```text
.github/workflows/ci.yml
```

Current automated test suite:

```text
40 tests
```

The CI pipeline helps ensure that changes do not break existing application behavior before they are integrated into the project.

## Project Structure

```text
Enterprise-IT-Service-Desk-Platform/
├── accounts/
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── tickets/
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── services.py
│   ├── urls.py
│   ├── views.py
│   └── tests/
│
├── assets/
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── tests/
│
├── config/
│   ├── exceptions.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── templates/
│   ├── accounts/
│   ├── tickets/
│   └── assets/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── compose.yaml
├── Dockerfile
├── manage.py
├── pytest.ini
├── requirements.txt
├── .env.example
└── README.md
```

### Application Responsibilities

- `accounts` — User accounts, departments, authentication-related APIs, and role information
- `tickets` — Ticket lifecycle, RBAC rules, workflow validation, ticket history, dashboard statistics, and service-layer business logic
- `assets` — IT asset inventory, assignment rules, department association, and asset permissions
- `config` — Django project configuration, global URL routing, REST framework configuration, and exception handling
- `templates` — Web interface for login, ticket operations, dashboard, and asset management
- `.github/workflows` — GitHub Actions continuous integration workflow

## Architecture

The project separates API handling, business rules, persistence, and infrastructure concerns.

```text
Client / Web UI
       │
       ▼
Django URL Routing
       │
       ▼
DRF API Views
       │
       ├── JWT Authentication
       ├── RBAC / Permissions
       │
       ▼
Serializers
       │
       ▼
Service Layer
       │
       ▼
Django ORM
       │
       ▼
MySQL
```

For ticket operations, business rules such as ticket creation, assignment, workflow transitions, and history recording are handled through the service layer instead of being concentrated entirely inside API views.

Cross-cutting concerns include:

- JWT authentication
- Role-based authorization
- Validation and exception handling
- Application logging
- Automated testing
- OpenAPI documentation
- Docker containerization
- GitHub Actions CI

## Testing

The project includes an automated Pytest test suite covering API permissions, RBAC rules, ticket workflow constraints, asset business rules, and history tracking.

Current test suite:

```text
40 tests
```

### Ticket API and RBAC

Tests verify that:

- The authenticated user is automatically used as the ticket reporter
- Employees can only access their own tickets
- Employees cannot submit privileged ticket fields
- IT Engineers can view operational ticket data but cannot assign tickets
- IT Managers can assign tickets to IT Engineers
- Non-engineer users cannot be assigned as ticket assignees
- Ticket history access respects user permissions
- Dashboard access is restricted to authorized IT roles

### Ticket Workflow

Tests verify that:

- Employees cannot change operational ticket status
- Only the assigned IT Engineer can start work on a ticket
- Invalid workflow transitions are rejected
- Tickets cannot be resolved without a resolution note
- Resolved tickets can be closed
- Resolved tickets cannot have their assignee removed
- Ticket updates automatically create history records
- Multiple field changes create corresponding history records

### Asset Management

Tests verify that:

- Employees only see assets assigned to themselves
- Employees cannot create or update assets
- IT staff can access the full asset inventory
- Assigning a user automatically changes the asset status to `in_use`
- Removing an assigned user changes an `in_use` asset back to `available`
- `in_use` assets require an assigned user
- Asset departments can be updated by IT staff
- Asset lists support search and filtering by status, asset type, and department

Run the complete test suite with:

```bash
pytest -v
```

## Future Improvements

The current version focuses on the core Service Desk backend architecture and business workflow. Possible future extensions include:

- Asynchronous background tasks with Celery
- Redis as a task broker / caching layer
- Email or in-app notifications for ticket events
- SLA tracking and escalation rules
- More detailed audit logging
- Advanced dashboard analytics and reporting
- Production deployment configuration