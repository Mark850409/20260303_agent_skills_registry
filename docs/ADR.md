# AI Skills & Apps Registry - 技術決策記錄 (ADR)

## 1. 架構選型：使用 Python Flask 作為 API 框架
- **狀態**：`[事實]` 已採用
- **背景**：需要一個輕量且易於與現有 Python 生態 (MCP SDK, AI 工具) 整合的後端框架。
- **考量選項**：
  - Node.js (Express/NestJS)
  - Python FastAPI
  - Python Flask
- **決策**：選擇了 Python Flask + Flask-Smorest，因專案需要快速開發 CRUD API，加上 Flask 有龐大的擴充套件 (如 SQLAlchemy/Marshmallow) 且團隊熟悉。
- **後果**：
  - **正面**：Python 處理許多 AI 相關套件與腳本較原生，API 文件 (Swagger) 能透過 Flask-Smorest 自動生成。
  - **負面**：在 Async/Await 與高併發支援上不如 FastAPI 優秀，需依賴 gunicorn/gevent 處理長連線。

## 2. 資料庫：使用 SQLite 作為預設資料庫
- **狀態**：`[事實]` 已採用
- **背景**：這是一個可自我託管 (Self-hosted) 的開源 Registry。
- **考量選項**：
  - PostgreSQL / MySQL
  - SQLite
- **決策**：預設使用 SQLite，透過 Docker Volume 掛載 (`/app/data/registry.db`) 來保存資料。
- **後果**：
  - **正面**：大幅降低使用者的部署複雜度，沒有額外的 Database Container 依賴。
  - **負面**：寫入鎖 (Write-lock) 可能在極高流量時成為瓶頸。
  - **因應**：透過 SQLAlchemy ORM，保留未來可輕鬆抽換為 PostgreSQL 的彈性。

## 3. 儲存：技能打包採用 `.tar.gz` 存檔於本地路徑
- **狀態**：`[事實]` 已採用
- **背景**：技能 (Skills) 本質上是一包 Markdown、Python 腳本與靜態檔案的組合。
- **決策**：在發布時 (Push)，CLI 會將路徑打包為 `.tar.gz` 並透過 API 上傳，API 再將其存放在 `data/` 目錄下對應的路徑中，資料庫 `skill_versions` 表內僅紀錄 `bundle_path` 與 `checksum`。
- **後果**：
  - **正面**：實作簡單，不依賴 S3 等雲端儲存，適合本地自建。
  - **風險**：若是多實例 (Multi-instance) 部署，需確保 `data/` 掛載為共享磁碟 (Shared Volume)。

## 4. MCP Server：支援 SSE 與 Stdio 混合配置
- **狀態**：`[事實]` 已採用
- **背景**：Model Context Protocol (MCP) 官方標準定義了兩種主要的客戶端連線方式：透過 HTTP 的 Server-Sent Events (SSE) 以及透過標準輸入輸出的 Stdio。
- **決策**：
  - 對於 `sse`，登錄檔僅保存遠端 URL (`endpoint_url`)。
  - 對於 `stdio`，不保存 URL，而是保存 `local_config` (一個 JSON Array，包含 npm/docker/pip 執行指令)。
- **後果**：CLI 指令 `agentskills mcp connect` 可以根據客戶端的支援程度與連線類型，自動組合出對應 `claude_desktop_config.json` 等配置檔所需的 JSON 區塊。
