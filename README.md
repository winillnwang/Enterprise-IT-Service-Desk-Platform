# Enterprise IT Service Desk Platform

企業 IT 維運暨工單管理平台，以 Django REST Framework 建置，模擬企業 Helpdesk／MIS 的工單生命週期、角色權限、資產管理、統計報表與系統管理流程。

本專案以完整業務規則與可驗證的權限控制為核心，而非只有 CRUD。Docker 定位為本機開發與作品展示環境，不宣稱為正式 Production 部署方案。

## 核心功能

- JWT 登入、Token 更新與目前使用者 API
- 四角色 Role-Based Access Control（RBAC）
- 工單建立、指派、狀態流程、結案說明與異動歷程
- 資產建立、指派、部門與狀態管理
- Dashboard 與統計報表
- 使用者、部門與工單分類管理
- OpenAPI Schema 與 Swagger UI
- 52 個 Pytest 自動化測試
- Docker Compose 與 GitHub Actions CI

## 系統架構

```text
Web UI / REST Client
        │
        ▼
Django URL Routing
        │
        ▼
DRF API Views
  ├─ JWT Authentication
  └─ RBAC Permissions
        │
        ▼
Serializers / Validation
        │
        ├─ Ticket Service Layer
        │   ├─ Assignment Rules
        │   ├─ Workflow Rules
        │   └─ History Recording
        ▼
Django ORM → MySQL
```

詳細架構請見 `docs/architecture.md`。

## 角色與權限

| 功能 | Employee | IT Engineer | IT Manager | Admin |
| --- | :---: | :---: | :---: | :---: |
| 建立工單 | ✅ | ✅ | ✅ | ✅ |
| 查看全部工單 | ❌ | ✅ | ✅ | ✅ |
| 執行工單流程 | ❌ | ✅ | ✅ | ✅ |
| 指派／重新指派工單 | ❌ | ❌ | ✅ | ✅ |
| Dashboard | ❌ | ✅ | ✅ | ✅ |
| 資產管理 | 僅查看自己的資產 | ✅ | ✅ | ✅ |
| 統計報表 | ❌ | ✅ | ✅ | ✅ |
| 系統管理 | ❌ | ❌ | ✅ | ✅ |

系統管理包含使用者、部門與工單分類的建立及更新。使用者採 `is_active` 停用機制，避免刪除帳號破壞歷史關聯與稽核資料。

## 工單流程

```text
open → assigned → in_progress → resolved → closed
```

- 新工單預設為 `open`。
- IT Manager／Admin 指派工程師後進入 `assigned`。
- 被指派的 IT Engineer 可開始處理並改為 `in_progress`。
- 轉為 `resolved` 前必須填寫 `resolution_note`。
- 狀態、負責人等重要欄位異動會寫入 Ticket History。
- 非法跳轉、偽造 Reporter／Assignee 或越權操作會被拒絕。

## 主要頁面

| URL | 用途 |
| --- | --- |
| `/login/` | 登入 |
| `/dashboard/` | IT Dashboard |
| `/tickets/` | 工單列表 |
| `/tickets/create/` | 建立工單 |
| `/tickets/<id>/` | 工單詳細與流程操作 |
| `/assets/` | 資產列表 |
| `/assets/create/` | 建立資產 |
| `/assets/<id>/` | 資產詳細與更新 |
| `/reports/` | 統計報表 |
| `/system/` | 使用者、部門與工單分類管理 |

所有主要後台頁面共用 `templates/base.html`、`static/css/app.css` 與 `static/js/layout.js`。Web UI 使用 localStorage JWT 呼叫 API；敏感資料與管理操作的最終授權由 DRF API 權限檢查執行。

## API Endpoints

### Authentication

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/api/auth/login/` | 取得 Access／Refresh Token |
| POST | `/api/auth/refresh/` | 更新 Access Token |
| GET | `/api/auth/me/` | 取得目前使用者 |

### Tickets、Dashboard 與 Reports

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/ticket-categories/` | 可用工單分類 |
| GET, POST | `/api/tickets/` | 查詢／建立工單 |
| GET, PATCH | `/api/tickets/<id>/` | 工單詳細／更新 |
| GET | `/api/tickets/<id>/history/` | 工單異動歷程 |
| GET | `/api/dashboard/summary/` | Dashboard 摘要 |
| GET | `/api/reports/summary/` | 報表摘要與篩選 |

### Assets

| Method | Endpoint | Description |
| --- | --- | --- |
| GET, POST | `/api/assets/` | 查詢／建立資產 |
| GET, PATCH | `/api/assets/<id>/` | 資產詳細／更新 |

### System Management

下列 API 僅允許 IT Manager 與 Admin：

| Method | Endpoint | Description |
| --- | --- | --- |
| GET, POST | `/api/admin/users/` | 查詢／建立使用者 |
| GET, PATCH | `/api/admin/users/<id>/` | 使用者詳細／更新 |
| GET, POST | `/api/admin/departments/` | 查詢／建立部門 |
| GET, PATCH | `/api/admin/departments/<id>/` | 部門詳細／更新 |
| GET, POST | `/api/admin/ticket-categories/` | 查詢／建立分類 |
| GET, PATCH | `/api/admin/ticket-categories/<id>/` | 分類詳細／更新 |

其他輔助 API：

```text
GET /api/users/it-staff/
GET /api/users/asset-assignees/
GET /api/departments/
```

OpenAPI Schema：`/api/schema/`

Swagger UI：`/api/docs/`

## 本機啟動

### 1. 建立虛擬環境並安裝套件

```bat
python -m venv venv2
venv2\Scripts\activate
pip install -r requirements.txt
```

### 2. 設定環境變數

```bat
copy .env.example .env
```

依本機環境調整 `.env`：

```text
DJANGO_SECRET_KEY=請替換成自己的金鑰
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=enterprise_it_service_desk_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=8888
```

`DJANGO_ALLOWED_HOSTS` 使用逗號分隔。正式環境必須提供獨立的 `DJANGO_SECRET_KEY`，並將 `DJANGO_DEBUG` 設為 `False`。

### 3. 建立資料表並啟動

```bat
python manage.py migrate
python manage.py runserver
```

應用程式：`http://127.0.0.1:8000/`

## Docker

```bat
copy .env.example .env
docker compose up --build
```

Compose 會啟動 Django 與 MySQL 8.4，並等待 MySQL healthcheck 通過後再啟動應用程式。容器預設使用 Django development server，適合本機開發與 Demo。

```bat
docker compose exec app python manage.py migrate
docker compose exec app python manage.py check
docker compose exec app pytest -v
docker compose down
```

## 測試與品質檢查

52 個測試涵蓋 Authentication、RBAC、Ticket API／Workflow／History、Dashboard、Reports、Asset Management 與 System Management。

```bat
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -v
```

目前驗證基準：

```text
System check identified no issues (0 silenced).
No changes detected
52 passed
```

## CI

`.github/workflows/ci.yml` 會在推送或 Pull Request 到 `master` 時啟動 MySQL 8.4、安裝依賴、執行 Django system check、檢查遺漏 migration，並執行完整測試。

## 專案結構

```text
Enterprise-IT-Service-Desk-Platform/
├─ accounts/
│  ├─ tests/test_system_management.py
│  ├─ models.py
│  ├─ serializers.py
│  ├─ system_management.py
│  └─ views.py
├─ tickets/
│  ├─ tests/
│  ├─ models.py
│  ├─ serializers.py
│  ├─ services.py
│  └─ views.py
├─ assets/
│  ├─ tests/
│  ├─ models.py
│  ├─ serializers.py
│  └─ views.py
├─ config/
│  ├─ exceptions.py
│  ├─ settings.py
│  └─ urls.py
├─ templates/
│  ├─ base.html
│  ├─ accounts/system_management.html
│  └─ tickets/reports.html
├─ static/
│  ├─ css/app.css
│  └─ js/layout.js
├─ docs/
│  ├─ architecture.md
│  └─ FINAL_ACCEPTANCE_CHECKLIST.md
├─ .github/workflows/ci.yml
├─ compose.yaml
├─ Dockerfile
└─ manage.py
```

## 安全性說明

- `.env`、Log、虛擬環境與測試快取均由 Git／Docker ignore 排除。
- Secret Key、Debug 與 Allowed Hosts 支援環境變數設定。
- 管理 API 同時要求 JWT 驗證與角色權限。
- 密碼透過 Django Password Hasher 儲存。
- localStorage JWT 適合作品 Demo；正式環境可再評估 HttpOnly Secure Cookie、Production WSGI server、HTTPS 與 CSP。

## 專案範圍

目前版本已進入 Feature Freeze。後續只處理文件、Demo、面試準備與錯誤修正，不納入 Celery、Redis、WebSocket、SLA Engine、CMDB 或大型通知系統。
