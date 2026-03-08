# AI Skills & Apps Registry 🧠

> 開源的 AI 技能與應用登錄平台，讓開發者發布、搜尋、安裝與分享 AI 工具與應用。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D.svg)](https://vuejs.org)

## 📦 專案結構

```
agent-skills-registry/
├── packages/
│   ├── registry-api/    # 後端 REST API（Python Flask）
│   ├── registry-ui/     # 前端網站（Vue.js 3 + Vite）
│   ├── cli/             # 命令列工具（agentskills）
│   └── skill-schema/    # Skill Bundle 規格與驗證器
├── skills/              # 官方範例 Skills
├── docs/                # 文件
└── docker-compose.yml
```

## 🚀 快速開始

### 安裝 CLI (NPM)

```bash
npm install -g agentskills
```

### CLI 指令

| 指令                                  | 說明                                  |
| ------------------------------------- | ------------------------------------- |
| `agentskills init <name>`             | 建立 Skill 骨架目錄                   |
| `agentskills login`                   | 儲存 API Token 至本地設定             |
| `agentskills push <path>`             | 打包並上傳 Skill Bundle               |
| `agentskills pull <name>[@version]`   | 下載並解壓 Skill Bundle               |
| `agentskills search <keyword>`        | 搜尋平台上的 Skills                   |
| `agentskills vendor <name>[@version]` | 將 Skill 鎖定到本地 vendor 目錄       |
| `agentskills vendor`                  | 從 lock file 還原所有 vendored Skills |
| `agentskills vendor --remove <name>`  | 移除已 vendor 的 Skill                |
| `agentskills mcp publish`             | 互動式發布 MCP Server                 |
| `agentskills mcp list`                | 列出已發布的 MCP Servers              |
| `agentskills mcp run <name>`          | 本地執行 MCP Server (Stdio)           |
| `agentskills mcp connect <name>`      | 獲取 MCP 連線配置                     |

### 從 Git 安裝

```bash
# 從 GitHub 安裝
agentskills pull github:user/my-skills

# 從任意 Git URL 安裝
agentskills pull https://github.com/user/my-skills.git

# 指定 Agent
agentskills pull web-search --agent cursor
agentskills pull web-search --global  # 全域安裝
```

## 🤖 支援的 Agents

| Agent          | 識別名稱         | 全域技能目錄                    |
| -------------- | ---------------- | ------------------------------- |
| Antigravity    | `antigravity`    | `~/.gemini/antigravity/skills/` |
| Claude Code    | `claude-code`    | `~/.claude/skills/`             |
| Cursor         | `cursor`         | `.cursor/skills/`               |
| Codex          | `codex`          | `.codex/skills/`                |
| OpenCode       | `opencode`       | `.opencode/skills/`             |
| GitHub Copilot | `github-copilot` | `.github/copilot/skills/`       |
| Roo Code       | `roo`            | `.roo/skills/`                  |

## 📁 Skill Bundle 結構

```
my-skill/
├── SKILL.md       ← 必填：YAML frontmatter + Markdown 指令
├── scripts/       ← 選填：Agent 可執行的腳本
├── references/    ← 選填：RAG / few-shot 參考文件
└── assets/        ← 選填：靜態模板與資源
```

## � 本地開發環境 (Docker)

本專案使用 Docker Compose 快速啟動完整環境。

```bash
# 1. 啟動所有服務（API & UI）
docker compose up -d --build

# 2. 初始化資料庫資料 (Seed)
docker compose exec api python scripts/seed.py
```

- **前端 UI**: [http://localhost:5173](http://localhost:5173)
- **後端 API**: [http://localhost:5006](http://localhost:5006)

---

## 🛠️ CLI 操作指南 (agentskills)

### 1. 安裝 CLI
在專案目錄下：
```bash
cd packages/cli
npm install -g .
```

### 2. 建立新的 Skill
```bash
# 建立一個名為 my-tool 的技能骨架
agentskills init my-cool-tool
```
> [!NOTE]
> 專案以強制使用 **UTF-8** 編碼寫入檔案，解決 Windows 環境下的亂碼問題。

### 3. 發布 Skill 到 Registry
進入 Skill 目錄編輯 `SKILL.md` 後，執行：
```bash
agentskills push ./my-cool-tool
```
發布成功後，可直接在瀏覽器造訪 [http://localhost:5173/skills/my-cool-tool](http://localhost:5173/skills/my-cool-tool) 查看。

### 4. 搜尋與下載
```bash
# 搜尋技能
agentskills search web-search

# 下載並安裝技能到當前專案
agentskills pull web-search --agent cursor
```

---

## 📦 套件發布與管理 (NPM & Docker)

### 發布 NPM 套件
1. **設定 Registry**:
   ```bash
   npm config set registry http://localhost:5005/npm
   ```
2. **登入與發布**:
   ```bash
   npm login
   npm publish
   ```
3. **刪除套件**:
   ```bash
   npm unpublish <package-name> --force
   ```

### 發布 Docker 鏡像
1. **登入 Registry**:
   ```bash
   docker login localhost:5005
   ```
2. **標記與推送**:
   ```bash
   docker tag my-image localhost:5005/my-repo:latest
   docker push localhost:5005/my-repo:latest
   ```
3. **移除本地緩存**:
   ```bash
   docker rmi localhost:5005/my-repo:latest
   ```

---

## 🖥️ GUI 介面功能

造訪 [http://localhost:5173](http://localhost:5173) 即可使用完整的 Web 介面：

1. **瀏覽與搜尋**: 支援關鍵字搜尋、標籤篩選與熱門度（下載數）排序。
2. **技能詳情**: 提供 Markdown 渲染的指令預覽、版本歷史、作者資訊與一鍵複製安裝指令。
3. **發布介面**: 支援 Skill (CLI/GitHub/表單) 與 MCP Server (SSE/Stdio) 的發布。
4. **管理後台**: 管理員可針對所有技能與 MCP 進行分類、編輯或刪除，支援 AI 自動分類。
5. **Agent 自動偵測**: 指導使用者如何將技能與 MCP 配置到不同的 AI Agents 中。

---

## 🔌 Model Context Protocol (MCP)

本平台全面支援 MCP 生態，讓您集中管理所有的工具。

### 發布 MCP
您可以使用 CLI 的互動指令進行發布，系統會自動在本地嘗試連線並「強制驗證」工具清單：
```bash
agentskills mcp publish
```
或是在 Web 介面的「發布」頁面切換到 MCP 分頁進行填寫。

### 連線 MCP
對於 SSE 類型，Registry 會自動處理 proxy，您只需獲取連線網址即可。對於 Stdio 類型，CLI 提供配置片段：
```bash
# 獲取適用於 Claude Desktop 的配置
agentskills mcp connect google-maps --agent claude
```

### 本地執行 (Debugging)
```bash
agentskills mcp run playwright-mcp
```

---

## 🤖 支援的 Agents (全域路徑)

| Agent       | 識別名稱      | 全域技能目錄                    |
| ----------- | ------------- | ------------------------------- |
| Antigravity | `antigravity` | `~/.gemini/antigravity/skills/` |
| Claude Code | `claude-code` | `~/.claude/skills/`             |
| Cursor      | `cursor`      | `.cursor/skills/`               |
| Roo Code    | `roo`         | `.roo/skills/`                  |

---

## 📄 License

MIT

