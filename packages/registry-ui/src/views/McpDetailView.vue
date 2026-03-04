<template>
  <div class="mcp-detail">
    <div class="detail-inner" v-if="mcp">
      <!-- Header -->
      <div class="detail-header card">
        <div class="detail-icon">{{ mcp.display_name?.[0]?.toUpperCase() }}</div>
        <div class="detail-info">
          <div class="detail-name-row">
            <h1 class="detail-name">{{ mcp.display_name }}</h1>
            <span v-if="mcp.is_verified" class="verified">✓ Verified</span>
            <span class="transport-pill" :class="mcp.transport">
              <span class="dot"></span>{{ transportLabel(mcp.transport) }}
            </span>
          </div>
          <div class="detail-slug">{{ mcp.author }}/{{ mcp.name }}</div>
          <p class="detail-desc">{{ mcp.description }}</p>
          <div class="detail-meta">
            <span v-if="mcp.category">{{ categoryIcon(mcp.category) }} {{ mcp.category }}</span>
            <span>⬇ {{ formatNum(mcp.installs) }} installs</span>
            <span v-if="mcp.license">📄 {{ mcp.license }}</span>
            <a v-if="mcp.repository" :href="mcp.repository" target="_blank" class="meta-link">🔗 Repository</a>
          </div>
          <!-- Tags -->
          <div v-if="mcp.tags?.length" class="detail-tags">
            <span v-for="t in mcp.tags" :key="t" class="tag">{{ t }}</span>
          </div>
        </div>
      </div>

      <div class="detail-body">
        <!-- Left: Tools -->
        <div class="tools-section card" v-if="mcp.tools?.length">
          <h2 class="section-title">🛠 提供的工具（{{ mcp.tools.length }}）</h2>
          <div v-for="tool in mcp.tools" :key="tool.name" class="tool-item">
            <div class="tool-name">{{ tool.name }}</div>
            <div class="tool-desc">{{ tool.description }}</div>
          </div>
        </div>

        <!-- Right: Connect Panel -->
        <div class="connect-panel card">
          <h2 class="section-title">🔗 連線此 MCP Server</h2>

          <!-- Tab 切換 -->
          <div class="connect-tabs">
            <button v-for="tab in availableTabs" :key="tab.id"
              class="conn-tab" :class="{ active: activeTab === tab.id }"
              @click="activeTab = tab.id">
              <span>{{ tab.icon }}</span> {{ tab.label }}
            </button>
          </div>

          <!-- Tab 內容 -->
          <div v-if="activeTab" class="tab-content">
            <p v-if="activeTab === 'remote'" class="tab-desc">直接使用 SSE 連線 URL 連接此 MCP Server：</p>
            <p v-else class="tab-desc">使用 {{ activeTab }} 在本機啟動此 MCP Server：</p>

            <!-- URL 或 Command Box -->
            <div class="conn-box">
              <div v-if="activeTab === 'remote'" class="conn-url-box">
                <span class="conn-url">{{ finalConnectUrl }}</span>
                <button class="copy-btn" @click="copy(finalConnectUrl)">📋</button>
              </div>
              <div v-else v-for="lc in currentConfigs" :key="lc.type" class="local-cmd-block">
                <div class="cmd-box">
                  <code>{{ lc.command }}</code>
                  <button class="copy-btn" @click="copy(lc.command)">📋</button>
                </div>
                <div v-if="lc.env?.length" class="env-list">
                  需設定環境變數：<span v-for="e in lc.env" :key="e" class="env-chip">{{ e }}</span>
                </div>
              </div>
            </div>

            <!-- 統一的 Agent 指南 -->
            <div class="agent-guides">
              <h3 class="guide-title">🚀 AI 工具安裝指南</h3>
              <div v-for="agent in AGENTS" :key="agent.id" class="agent-item">
                <div class="agent-header" @click="toggleAgent(agent.id)">
                  <div class="agent-header-left">
                    <span class="agent-icon">{{ agent.icon }}</span>
                    <div class="agent-name-box">
                      <div class="agent-name">{{ agent.name }}</div>
                      <div class="agent-desc">{{ agent.desc }}</div>
                    </div>
                  </div>
                  <span class="agent-toggle">{{ openAgent === agent.id ? '▲' : '▼' }}</span>
                </div>
                <div v-if="openAgent === agent.id" class="agent-steps">
                  <div v-html="agent.render()"></div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="copied" class="copy-success">✓ 已複製</div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-else-if="loading" class="loading-state">載入中…</div>
    <div v-else class="empty-state">找不到此 MCP Server</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { mcpApi } from '@/api'

const route = useRoute()
const name  = route.params.name

const mcp         = ref(null)
const connectInfo = ref(null)
const loading     = ref(true)
const activeTab   = ref('')
const openAgent   = ref(null)
const copied      = ref(false)

// 可用 Tab（依 transport + local_config 動態顯示）
const availableTabs = computed(() => {
  const tabs = []
  const m = mcp.value
  if (m && (m.endpoint_url || m.transport === 'sse' || m.transport === 'http')) {
    tabs.push({ id: 'remote', icon: '📡', label: 'Remote SSE' })
  }
  const types = new Set((m?.local_config || []).map(c => c.type))
  if (types.has('docker')) tabs.push({ id: 'docker', icon: '🐳', label: 'Docker' })
  if (types.has('python')) tabs.push({ id: 'python', icon: '🐍', label: 'Python' })
  if (types.has('node'))   tabs.push({ id: 'node',   icon: '🟢', label: 'Node.js' })
  return tabs
})

const dockerConfigs = computed(() => (mcp.value?.local_config || []).filter(c => c.type === 'docker'))
const pythonConfigs = computed(() => (mcp.value?.local_config || []).filter(c => c.type === 'python'))
const nodeConfigs   = computed(() => (mcp.value?.local_config || []).filter(c => c.type === 'node'))

const currentConfigs = computed(() => {
  if (activeTab.value === 'docker') return dockerConfigs.value
  if (activeTab.value === 'python') return pythonConfigs.value
  if (activeTab.value === 'node') return nodeConfigs.value
  return []
})

// SSE URL
const sseProxyUrl = computed(() => `${window.location.origin}/api/mcps/${name}/sse`)

// 最終連線 URL
const finalConnectUrl = computed(() => {
  const e = connectInfo.value?.endpoint_url
  const path = `/api/mcps/${name}/sse`
  if (e && e.includes(path)) return sseProxyUrl.value
  return e || sseProxyUrl.value
})

const AGENTS = computed(() => {
  const m = mcp.value
  if (!m) return []
  
  const url = finalConnectUrl.value
  const mcpName = m.name
  const isSSE = m.transport === 'sse' || m.transport === 'http'
  
  const currentStdio = activeTab.value !== 'remote' ? currentConfigs.value[0] : null
  const stdioJson = activeTab.value === 'docker' ? dockerClaudeConfig.value :
                    activeTab.value === 'python' ? pythonClaudeConfig.value :
                    activeTab.value === 'node' ? nodeClaudeConfig.value : null

  return [
    {
      id: 'agentskills', icon: '🧠', name: 'AgentSkills CLI',
      desc: '使用本專案原創 CLI 快速管理',
      render: () => `
        <div class="install-guide">
          <p>在終端機執行指令即可自動安裝並設定：</p>
          <div class="cmd-box">
            <code>agentskills mcp add ${mcpName} ${isSSE ? `--url ${url}` : '--local'}</code>
          </div>
        </div>`
    },
    {
      id: 'claude-desktop', icon: '🟠', name: 'Claude Desktop',
      desc: '官方桌面客戶端',
      render: () => isSSE ? `
        <ol>
          <li>開啟 Claude Desktop → <strong>Settings > Connectors</strong></li>
          <li>點擊 <strong>Add custom connector</strong></li>
          <li>貼上 Server URL：<code>${url}</code></li>
        </ol>` : `
        <ol>
          <li>開啟設定檔：<code>claude_desktop_config.json</code></li>
          <li>在 <code>mcpServers</code> 區塊加入以下內容：</li>
        </ol>
        <pre class="code-block">${stdioJson}</pre>`
    },
    {
      id: 'cursor', icon: '🖱', name: 'Cursor',
      desc: 'AI 優先的編輯器',
      render: () => isSSE ? `
        <ol>
          <li>開啟 Cursor → <strong>Settings > MCP</strong></li>
          <li>新增 SSE Server，URL：<code>${url}</code></li>
        </ol>` : `
        <ol>
          <li>開啟 Cursor → <strong>Settings > MCP</strong></li>
          <li>新增 stdio Server：</li>
          <li>Command: <code>${parseStdio(currentStdio).command}</code></li>
          <li>Args: <code>${JSON.stringify(parseStdio(currentStdio).args)}</code></li>
        </ol>`
    },
    {
      id: 'vscode', icon: '🔵', name: 'VS Code (Copilot)',
      desc: 'GitHub Copilot 擴充功能',
      render: () => `
        <p>在 <code>settings.json</code> 加入：</p>
        <pre class="code-block">${JSON.stringify({ 
          "github.copilot.chat.experimental.mcp": { 
            "servers": { [mcpName]: isSSE ? { url } : parseStdio(currentStdio) } 
          } 
        }, null, 2)}</pre>`
    },
    {
      id: 'claudecode', icon: '📟', name: 'Claude Code',
      desc: 'Anthropic 官方 CLI',
      render: () => `
        <div class="cmd-box">
          <code>agentskills mcp add ${mcpName} --target claudecode</code>
        </div>`
    },
    {
      id: 'antigravity', icon: '🚀', name: 'Antigravity',
      desc: '高效能 AI 開發平台',
      render: () => `
        <div class="cmd-box">
          <code>agentskills mcp add ${mcpName} --target antigravity</code>
        </div>`
    },
    {
      id: 'kiro', icon: '🦊', name: 'Kiro',
      desc: '輕量級 AI 助手',
      render: () => `
        <div class="cmd-box">
          <code>agentskills mcp add ${mcpName} --target kiro</code>
        </div>`
    }
  ]
})

function parseStdio(lc) {
  if (!lc) return { command: '', args: [] }
  if (activeTab.value === 'docker') return { command: 'docker', args: ['run', '-i', '--rm', ...(lc.env||[]).flatMap(e=>['-e',`${e}=<${e}>`]), lc.image || ''] }
  if (activeTab.value === 'python') {
    const pkg = lc.package?.replace(/-/g,'_').split('/').pop() || ''
    return { command: 'python', args: ['-m', pkg] }
  }
  if (activeTab.value === 'node') return { command: 'npx', args: ['-y', lc.package || ''] }
  return { command: '', args: [] }
}

const dockerClaudeConfig = computed(() => {
  const lc = dockerConfigs.value[0]; if (!lc) return ''
  return JSON.stringify({ mcpServers: { [name]: parseStdio(lc) }}, null, 2)
})

const pythonClaudeConfig = computed(() => {
  const lc = pythonConfigs.value[0]; if (!lc) return ''
  const cfg = parseStdio(lc)
  if (lc.env?.length) cfg.env = Object.fromEntries(lc.env.map(e=>[e, `<${e}>`]))
  return JSON.stringify({ mcpServers: { [name]: cfg }}, null, 2)
})

const nodeClaudeConfig = computed(() => {
  const lc = nodeConfigs.value[0]; if (!lc) return ''
  const cfg = parseStdio(lc)
  if (lc.env?.length) cfg.env = Object.fromEntries(lc.env.map(e=>[e, `<${e}>`]))
  return JSON.stringify({ mcpServers: { [name]: cfg }}, null, 2)
})

function toggleAgent(id) { openAgent.value = openAgent.value === id ? null : id }

async function copy(text) {
  if (!text) return
  await navigator.clipboard.writeText(text)
  copied.value = true
  setTimeout(() => copied.value = false, 1500)
}

function transportLabel(t) {
  return { sse: 'Remote SSE', stdio: 'Stdio', http: 'HTTP' }[t] || t || 'Remote'
}

function categoryIcon(cat) {
  const icons = { web_search:'🔍', browser:'🌐', data:'📊', coding:'💻', productivity:'⚡', ai:'🤖', database:'🗄️', communication:'💬', cloud:'☁️' }
  return icons[cat] || '🧩'
}

function formatNum(n) {
  if (!n) return '0'
  if (n >= 1000) return (n/1000).toFixed(1)+'k'
  return String(n)
}

onMounted(async () => {
  try {
    const [mcpRes, connRes] = await Promise.all([
      mcpApi.get(name),
      mcpApi.connect(name),
    ])
    mcp.value         = mcpRes.data
    connectInfo.value = connRes.data
    if (availableTabs.value.length) {
      activeTab.value = availableTabs.value[0].id
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.mcp-detail { max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }
.detail-inner { display: flex; flex-direction: column; gap: 1.2rem; }

.detail-header { display: flex; gap: 1.25rem; padding: 1.5rem; }
.detail-icon { width: 64px; height: 64px; border-radius: 14px; background: linear-gradient(135deg, rgba(249,115,22,0.25), rgba(251,146,60,0.1)); border: 1px solid rgba(249,115,22,0.3); display: flex; align-items: center; justify-content: center; font-size: 1.6rem; font-weight: 700; color: #f97316; flex-shrink: 0; }
.detail-info { flex: 1; }
.detail-name-row { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 0.25rem; }
.detail-name { font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; font-weight: 700; margin: 0; }
.verified { font-size: 0.78rem; background: rgba(249,115,22,0.15); color: #f97316; border: 1px solid rgba(249,115,22,0.3); border-radius: 10px; padding: 2px 9px; }
.transport-pill { display: flex; align-items: center; gap: 4px; font-size: 0.78rem; padding: 2px 10px; border-radius: 10px; background: rgba(249,115,22,0.1); color: #f97316; border: 1px solid rgba(249,115,22,0.2); }
.dot { width: 6px; height: 6px; border-radius: 50%; background: #f97316; }
.detail-slug { font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.6rem; }
.detail-desc { color: var(--text-secondary); font-size: 0.9rem; line-height: 1.6; margin: 0 0 0.75rem; }
.detail-meta { display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem; }
.meta-link { color: var(--accent); text-decoration: none; }
.detail-tags { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.tag { font-size: 0.72rem; padding: 2px 8px; border-radius: 10px; border: 1px solid var(--border); background: var(--bg-secondary); color: var(--text-muted); }

.detail-body { display: grid; grid-template-columns: 320px 1fr; gap: 1.2rem; }
.section-title { font-size: 1rem; font-weight: 700; margin: 0 0 1rem; }
.tools-section { padding: 1.25rem; }
.tool-item { padding: 0.65rem 0; border-bottom: 1px solid var(--border-subtle); }
.tool-item:last-child { border-bottom: none; }
.tool-name { font-weight: 600; font-size: 0.88rem; font-family: 'JetBrains Mono', monospace; color: #f97316; }
.tool-desc { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem; }

/* Connect Panel */
.connect-panel { padding: 1.25rem; }
.connect-tabs { display: flex; gap: 2px; border-bottom: 1px solid var(--border); margin-bottom: 1rem; }
.conn-tab { padding: 0.5rem 0.85rem; border: none; background: transparent; color: var(--text-muted); font-size: 0.82rem; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.15s; display: flex; gap: 0.3rem; align-items: center; }
.conn-tab:hover { color: #f97316; }
.conn-tab.active { color: #f97316; border-bottom-color: #f97316; font-weight: 600; }

.tab-content { display: flex; flex-direction: column; gap: 1rem; }
.tab-desc { font-size: 0.85rem; color: var(--text-muted); margin: 0; }

.conn-url-box, .cmd-box { display: flex; align-items: center; gap: 0.5rem; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 8px; padding: 0.6rem 1rem; }
.conn-url, .cmd-box code { flex: 1; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: var(--text-primary); word-break: break-all; }
.copy-btn { background: transparent; border: none; cursor: pointer; font-size: 1rem; padding: 0; color: var(--text-muted); transition: color 0.2s; }
.copy-btn:hover { color: #f97316; }

.env-list { font-size: 0.78rem; color: var(--text-muted); display: flex; gap: 0.4rem; align-items: center; flex-wrap: wrap; margin-top: 0.6rem; }
.env-chip { font-family: 'JetBrains Mono', monospace; background: rgba(249,115,22,0.1); color: #f97316; padding: 1px 6px; border-radius: 4px; border: 1px solid rgba(249,115,22,0.2); }

/* Agent Guides */
.agent-guides { margin-top: 1.5rem; border-top: 1px solid var(--border); padding-top: 1.5rem; display: flex; flex-direction: column; gap: 0.6rem; }
.guide-title { font-size: 0.95rem; font-weight: 700; margin: 0 0 0.5rem; color: var(--text-primary); }
.agent-item { border: 1px solid var(--border); border-radius: 10px; overflow: hidden; background: var(--bg-secondary); }
.agent-header { display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1rem; cursor: pointer; transition: background 0.2s; }
.agent-header:hover { background: var(--bg-card); }
.agent-header-left { display: flex; gap: 0.85rem; align-items: center; }
.agent-icon { font-size: 1.25rem; }
.agent-name { font-size: 0.88rem; font-weight: 600; color: var(--text-primary); }
.agent-desc { font-size: 0.75rem; color: var(--text-muted); margin-top: 2px; }
.agent-toggle { color: var(--text-muted); font-size: 0.8rem; }

.agent-steps { padding: 1rem; background: var(--bg-primary); border-top: 1px solid var(--border); font-size: 0.85rem; color: var(--text-secondary); line-height: 1.7; }
.agent-steps :deep(ol), .agent-steps :deep(ul) { margin: 0; padding-left: 1.25rem; }
.agent-steps :deep(code) { font-family: 'JetBrains Mono', monospace; background: var(--bg-secondary); padding: 2px 6px; border-radius: 4px; font-size: 0.78rem; border: 1px solid var(--border); }
.agent-steps :deep(.code-block) { display: block; margin: 0.5rem 0; padding: 0.75rem; background: #1e1e1e; color: #d4d4d4; border-radius: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; overflow-x: auto; border: 1px solid #333; }
.agent-steps :deep(.cmd-box) { margin-top: 0.5rem; }

.copy-success { text-align: center; color: #f97316; font-size: 0.82rem; font-weight: 600; margin-top: 0.5rem; }
.loading-state, .empty-state { text-align: center; padding: 5rem; color: var(--text-muted); }

@media (max-width: 768px) {
  .detail-header { flex-direction: column; }
  .detail-body { grid-template-columns: 1fr; }
}
</style>
