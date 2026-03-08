# AI Skills & Apps Registry - 需求規格書 (PRD)

## 1. 產品概述
**產品名稱**：AI Skills & Apps Registry
**產品定位**：這是一套開源的 AI 技能與應用登錄平台（Registry），旨在讓開發者發布、搜尋、安裝與分享 AI 工具、Agentic Skills 以及 Model Context Protocol (MCP) Servers。
**目標市場與使用者**：
- **AI Agent 開發者 / 使用者**：需要為自家的 Agent (如 Antigravity, Claude Code, Cursor) 尋找並安裝擴充技能或 MCP Server。
- **工具開發者**：開發了實用的 AI 工具腳本或 MCP 伺服器，希望分享給開源社群或內部團隊使用。
- **系統管理員**：負責維護內部 AI 工具庫、審核發布的技能與管理使用者權限。

## 2. 使用者角色 (Personas)
1. **一般使用者 (User / Consumer)**：
   - 目標：搜尋並下載所需的 Skill 或 MCP Server。
   - 痛點：不知道有哪些指令可用，難以將工具整合進各種不同的 Agent IDE 中。
2. **技能作者 (Author / Publisher)**：
   - 目標：打包並發布自己的 Python/Node.js 腳本或 MCP Server 到平台上。
   - 痛點：缺乏統一的發布平台，難以追蹤工具的下載數量與版本歷史。
3. **系統管理員 (Admin)**：
   - 目標：管理平台上的所有技能、MCP Server 與使用者，維護平台內容品質。
   - 痛點：需要快速審核、分類或下架不當內容，並處理使用者權限。

## 3. 功能需求清單
### 3.1 技能 (Skill) 管理
- **[Must Have]** 查詢與瀏覽技能清單 (支援關鍵字搜尋、標籤與分類篩選)。
- **[Must Have]** 查看單一技能詳細資訊 (指令說明、作者、下載數、版本歷史、README 展示)。
- **[Must Have]** 透過 CLI 打包發布新技能 (Push) 或新版本。
- **[Must Have]** 透過 CLI 下載並安裝技能到指定 Agent 的全域目錄 (Pull)。

### 3.2 MCP Server 管理
- **[Must Have]** 查詢與瀏覽 MCP Servers 清單。
- **[Must Have]** 透過 CLI 或 Web 介面互動式發布 MCP Server (支援 SSE 或 Stdio 傳輸)。
- **[Must Have]** 透過 CLI 取回 MCP 連線配置，支援多種主流 IDE (Claude Desktop, Cursor, etc.)。
- **[Should Have]** 在 CLI 端本地除錯執行 MCP Server (Run)。

### 3.3 使用者與權限管理
- **[Must Have]** 使用者註冊與登入。
- **[Must Have]** CLI 端保存 API Token 進行身分驗證。
- **[Must Have]** 基於角色的權限存取控制 (RBAC) - 區分 `admin`, `maintainer`, `user`。

### 3.4 管理後台 (Admin Panel)
- **[Must Have]** 管理員可檢視、編輯、刪除全站技能與 MCP Servers。
- **[Must Have]** 批次刪除技能與 MCP Servers (根據前次對話紀錄新增)。
- **[Should Have]** 自動為內容套用分類 (AI 分類輔助)。
- **[Should Have]** 管理員管理使用者權限 (User Management)。

## 4. 非功能需求
- **相容性**：CLI 需支援 Windows、macOS 與 Linux 環境。
- **整合性**：需支援自動將 MCP 配置寫入主流 IDE (Antigravity, Claude Code, Cursor, VS Code 等) 的設定檔。
- **部署性**：支援透過 Docker Compose 一鍵部署完整前後端與資料庫。
- **效能**：在 Registry 增加到數千個項目時，搜尋 API 仍需在 100ms 內回傳。

## 5. 已知限制與假設
- 假設大多數的 Agent IDE 其全域設定路徑為已知且固定的 (例如 `~/.claude/skills/`)。
- 專案使用 HTTP SSE (Server-Sent Events) 作為部分 MCP 的連線方式，需要反向代理 (Nginx) 支援長連線。

## 6. 待確認問題清單
- `[待確認]` 目前的 Docker 部署方式是否考慮跨多台伺服器的高可用性 (HA) 架構？
- `[待確認]` 平台是否需要實作付費或私有 (Private) 模組的存取權限控管？
