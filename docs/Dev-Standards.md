# AI Skills & Apps Registry - 開發規範 (Dev Standards)

## 1. 命名規範
### **現況與標準**
- **API 路徑**: 採取全小寫與 Restful 複數名詞。例如 `/api/skills`, `/api/mcps`。
- **檔案/資料夾名稱**: 
  - Python (Backend/CLI): 使用 `snake_case` (e.g. `mcp_server_sse.py`)
  - Vue (Frontend): Components 用 `PascalCase` (e.g. `SkillCard.vue`)，Views 用 `kebab-case`。
- **變數與類別**:
  - Python: 變數與函式用 `snake_case`，Class 用 `PascalCase`。
  - JavaScript/TypeScript: 變數與函式用 `camelCase`，元件或 Class 用 `PascalCase`。

### **原因**
- 遵循語言各自的官方標準以確保團隊一致性與 IDE 自動排版正確。

---

## 2. API 開發規範
### **現況與標準**
- **現況**: 使用 Flask-Smorest 處理 Schema Validations 與 Swagger OpenAPI 產出。
- **新功能標準**: 
  - 新增 API 路由必須定義在 `app/schemas.py` 中的 Request & Response Schema，不手動解析 `request.json`。
  - **回傳格式統一**: 成功/失敗訊息應盡量遵循 standard JSON API 格式，對於 400 錯誤需包含 `{ "errors": { ... } }`。
  - **權限控制**: 所有具備寫入性質的 API 都必須加上 `@jwt_required()` 裝飾器，並適時檢查擁有者/管理員身分。

### **原因**
- 自動化文件生成能省去手寫 API Spec 的時間，並確保 Schema 驗證與文件永遠同步。

---

## 3. 資料庫與 ORM 規範
### **現況與標準**
- **現況**: 透過 SQLAlchemy 實作模型並使用 Flask-Migrate 進行資料庫遷移。
- **新功能標準**: 
  - 禁止在發布後直接修改 `models.py` 卻不產出 Migration 腳本。
  - 每個有查詢條件的欄位 (例如 `name`, `category`) 加上 `index=True`。

### **原因**
- 在 SQLite/PostgreSQL 混合支援架構下，透過 ORM 能避免 SQL 注入並保證 Schema 更新的原子性。

---

## 4. 前端架構規範
### **現況與標準**
- **現況**: 使用 Vue 3 + Tailwind CSS。
- **新功能標準**: 
  - 全域狀態存放於 Pinia (`stores/` 目錄)。
  - API 呼叫全部集中封裝於 `services/api.js`，避免在 Vue 元件內直接呼叫 `axios.get`。
  - 使用 `@vueuse/core` 來處理常見 Browser API 狀態整合。

### **原因**
- 統一資料獲取來源，如果未來需更換 axios 到 fetch 或更換 token 刷新機制，僅需修改一處。

---

## 5. CLI 開發規範
### **現況與標準**
- **現況**: CLI 為一個獨立 Python Package，與 API 並無直接在程式碼上的相依套件。
- **新檔案與讀寫**: 設定檔 (`~/.agentskills/config.json`) 或寫入任何檔案時，必須指定 `encoding="utf-8"`。

### **原因**
- 確保在 Windows 環境下處理帶有中文的 `SKILL.md` 說明時，不會發生 `UnicodeDecodeError`。
