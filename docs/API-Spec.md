# AI Skills & Apps Registry - API 規格文件

## 1. API 總覽
- **Base URL**: `http://localhost:5006/api` (開發環境)
- **傳輸格式**: 所有的 Request 與 Response Body 皆預設為 `application/json`。
- **認證方式**: 使用 Bearer JWT Token (`Authorization: Bearer <TOKEN>`)。
- **分頁規範**: 查詢列表列表 API 支援 `?page=1&per_page=20` 參數，回傳 `{ "items": [], "total": 100, "page": 1, "pages": 5, "per_page": 20 }`。

## 2. 認證說明
開發者可透過 CLI 執行 `agentskills login` 或透過 Web UI 取得 API Token。
取得 Token 後放入 Header：
```http
Authorization: Bearer my-jwt-token
```
- **角色層級**：
  - `user`: 可發布、更新自己擁有的技能或 MCP。
  - `admin`: 可修改、刪除任何人的資源，並管理使用者帳號。

## 3. 錯誤碼定義
- `400 Bad Request`: 請求格式或參數錯誤 (如 Validation Error)。
- `401 Unauthorized`: 缺少 Token 或 Token 無效。
- `403 Forbidden`: 權限不足，例如嘗試修改非本人上傳的資源。
- `404 Not Found`: 請求的資源 (Skill, MCP Server, User) 不存在。
- `409 Conflict`: 名稱已存在，例如發布了重複名稱的技能。
- `422 Unprocessable Entity`: Semantic 驗證失敗 (Smorest 預設)。

## 4. Endpoint 目錄

### 4.1 Auth 認證 API
#### `POST /auth/login`
- **功能**: 使用帳號密碼登入換取 Token。
- **Request Body**:
  ```json
  { "username": "user1", "email": "user1@example.com" }
  ```
- **Response**(200):
  ```json
  { "api_token": "jwt.token.string", "username": "user1" }
  ```

#### `GET /auth/me`
- **功能**: 取得當前 Token 的使用者狀態與權限。
- **Headers**: `Authorization: Bearer <token>`
- **Response**(200):
  ```json
  { "username": "user1", "role": "admin", "permissions": ["..."] }
  ```

### 4.2 Skills 技能 API
#### `GET /skills`
- **功能**: 列出平台上的所有技能。
- **Query Params**: `q` (關鍵字), `tags`, `category`, `sort` (預設 `downloads`)
- **Response**(200): 
  回傳 `SkillListResponseSchema` (包含 `skills` 陣列與分頁資訊)。

#### `GET /skills/<skill_id>`
- **功能**: 取得單一技能詳情。
- **Response**(200):
  回傳包含 `versions`, `skill_md` 等完整資訊的 JSON。

#### `POST /skills`
- **功能**: 推送 (Push) 或建立新技能與新版本。
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**: 需符合 `SkillPushSchema`，包含 `name`, `version`, `description`, `skill_md`, `author` 等。
- **Response**(201/200): 技能建立成功訊息與 ID。

#### `DELETE /skills/<skill_id>`
- **功能**: 刪除指定技能 (僅限擁有者或 Admin)。
- **Headers**: `Authorization: Bearer <token>`

### 4.3 MCP Servers API
#### `GET /mcps`
- **功能**: 列出所有登錄的 MCP Servers。
- **Query Params**: `q`, `category`, `tags`, `transport` (`sse`|`stdio`)

#### `POST /mcps`
- **功能**: 互動式發布或登錄一個 MCP Server。
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  包含 `name`, `display_name`, `transport`, `tools` 陣列與 `local_config` (若是 stdio) 或 `endpoint_url` (若是 sse)。

#### `DELETE /mcps/<mcp_id>`
- **功能**: 刪除指定的 MCP Server。

### 4.4 Admin 後台管理 API
#### `GET /admin/users`
- **權限**: 僅限 `admin` 角色。
- **功能**: 取得所有使用者清單。

#### `POST /admin/skills/batch-delete`
- **功能**: 批次刪除技能。
- **Request Body**: `{ "ids": [1, 2, 3] }`

#### `POST /admin/mcps/batch-delete`
- **功能**: 批次刪除 MCP 伺服器。
- **Request Body**: `{ "ids": [1, 2, 3] }`
