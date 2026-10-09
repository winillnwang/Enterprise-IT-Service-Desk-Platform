# Enterprise IT Service Desk Platform

## Final Acceptance Checklist

本文件用於封版前的人工驗收。自動化檢查可驗證主要 API、業務規則與權限；瀏覽器呈現、互動流程及不同螢幕尺寸仍需人工確認。

## 1. 自動化封版檢查

在專案根目錄執行：

```bat
python manage.py check
python manage.py makemigrations --check --dry-run
pytest -v
```

預期結果：

```text
System check identified no issues (0 silenced).
No changes detected
52 passed
```

## 2. 測試帳號準備

準備四個角色的測試帳號；帳號名稱可依本機資料調整：

| Role | 建議帳號 |
| --- | --- |
| Employee | `employee01` |
| IT Engineer | `it_engineer01` |
| IT Manager | `it_manager01` |
| Admin | `admin` |

請勿將正式密碼寫入 README、Git 或驗收文件。

## 3. Role-Based Access Control

### Employee

- [ ] 登入後可進入工單列表及建立工單。
- [ ] 只能看到自己的工單及自己的資產。
- [ ] 建立工單時不能指定 Reporter、Assignee 或 Status。
- [ ] 無法指派工單或變更工單流程狀態。
- [ ] Sidebar 不顯示 Dashboard、統計報表與系統管理。
- [ ] 呼叫 `/api/dashboard/summary/`、`/api/reports/summary/` 及 `/api/admin/*` 會得到 `403 Forbidden`。

### IT Engineer

- [ ] 可查看全部工單、Dashboard、Reports 與資產資料。
- [ ] 可處理指派給自己的工單及填寫 Resolution Note。
- [ ] 無法將工單指派給其他工程師。
- [ ] Sidebar 不顯示系統管理。
- [ ] 呼叫 `/api/admin/*` 會得到 `403 Forbidden`。

### IT Manager

- [ ] 可查看全部工單並指派／重新指派給合法 IT Engineer。
- [ ] 可使用 Dashboard、Reports 與資產管理。
- [ ] 可進入 `/system/`。
- [ ] 可建立／更新使用者、部門與工單分類。
- [ ] 新增使用者的密碼以 Django Password Hasher 儲存。

### Admin

- [ ] 可使用全部工單、資產、報表及系統管理功能。
- [ ] 可建立／更新使用者、部門與工單分類。
- [ ] 不受 Employee 或 IT Engineer 的操作限制。

## 4. Ticket Workflow

依序完成一次完整流程：

```text
open → assigned → in_progress → resolved → closed
```

- [ ] 建立工單後狀態為 `open`。
- [ ] IT Manager／Admin 指派後狀態為 `assigned`。
- [ ] 被指派的 IT Engineer 可改為 `in_progress`。
- [ ] 沒有 Resolution Note 時不能改為 `resolved`。
- [ ] 填寫 Resolution Note 後可改為 `resolved`。
- [ ] `resolved` 可改為 `closed`。
- [ ] 每次重要欄位異動都有 Ticket History。
- [ ] 非法跳轉與未指派工程師操作會被拒絕。

## 5. System Management

### 使用者管理

- [ ] 新增使用者並設定 Role、Department 與 Active 狀態。
- [ ] 編輯 Role、Department、Active 狀態後重新整理，資料仍正確。
- [ ] 修改密碼後可用新密碼登入。
- [ ] Employee 與 IT Engineer 無法透過直接 API URL 越權操作。

### 部門管理

- [ ] 新增部門，確認 Code、Name、Description 正確。
- [ ] 更新部門後重新整理，資料仍正確。
- [ ] 重複 Code／Name 時顯示合理驗證訊息。

### 工單分類

- [ ] 新增分類，確認 Code、Name、Description、Active 狀態正確。
- [ ] 更新及停用分類後重新整理，資料仍正確。
- [ ] 停用分類不會出現在一般建立工單的可用分類中。

## 6. Reports

- [ ] `/reports/` 可正常載入摘要與圖表。
- [ ] Start Date、End Date、Department 篩選可用。
- [ ] Status、Priority 與月份統計會隨篩選條件更新。
- [ ] 無效日期格式回傳 `400 Bad Request`。
- [ ] Employee 無法讀取報表 API。

## 7. Asset Management

- [ ] Employee 只看到指派給自己的資產，且不能建立或更新。
- [ ] IT 角色可建立與更新資產。
- [ ] 指派使用者後資產狀態自動成為 `in_use`。
- [ ] 移除使用者後 `in_use` 資產回到 `available`。
- [ ] Search、Status、Type 與 Department 篩選正常。

## 8. UI 與 Responsive

逐頁確認：

- [ ] Login
- [ ] Dashboard
- [ ] Ticket List
- [ ] Ticket Create
- [ ] Ticket Detail
- [ ] Asset List
- [ ] Asset Create
- [ ] Asset Detail
- [ ] Reports
- [ ] System Management

每頁共同檢查：

- [ ] 共用 Sidebar、Topbar、按鈕、卡片、表格與表單風格一致。
- [ ] Sidebar active 狀態與角色選單正確。
- [ ] 使用者名稱與角色顯示於右上角。
- [ ] 表格在窄畫面可水平捲動，不遮住內容。
- [ ] Mobile Menu 可展開與收合。
- [ ] 瀏覽器 Console 無 JavaScript Error、CSS／JS 404 或無限 Token Refresh。

建議至少使用桌面 `1920 × 1080` 與一個小型視窗各驗收一次。

## 9. Docker

- [ ] `.env` 已由 `.env.example` 建立且沒有提交到 Git。
- [ ] `docker compose config` 可成功解析。
- [ ] `docker compose up --build` 可正常啟動。
- [ ] MySQL healthcheck 通過後 Django 才啟動。
- [ ] 容器內可執行 migrate、check 與 pytest。

## 10. Git 與交付內容

- [ ] `.env`、`app.log`、`venv2/`、`__pycache__/`、`.pytest_cache/` 未被追蹤。
- [ ] `git diff --check` 無空白字元錯誤。
- [ ] `git status` 只包含本次預期變更。
- [ ] 提交並推送後 Working Tree Clean。
- [ ] 對外作品 ZIP 不包含 `.git/`、`.env`、Log、虛擬環境或快取。

## Definition of Done

以下全部完成後即可封版：

- [ ] Django check passed
- [ ] Migration check passed
- [ ] 52 tests passed
- [ ] 四角色權限驗收完成
- [ ] Ticket、Asset、Reports、System Management 手動流程完成
- [ ] 十個主要頁面的 UI 與 Responsive 驗收完成
- [ ] README、架構文件與環境變數範例一致
- [ ] Git 工作目錄乾淨且遠端版本已更新

封版後只處理 Bug Fix、文件、Demo 與面試準備；不擴充 Celery、Redis、WebSocket、SLA Engine、CMDB 或大型通知系統。
