<template>
  <div class="home">
    <!-- ── Hero ── -->
    <section class="hero fade-up">
      <div class="hero-inner">
        <div class="hero-badge">開源 · 免費 · 社群驅動</div>
        <h1 class="hero-title">
          探索 AI Skills & Apps<br />
          <span class="hero-accent">Registry</span>
        </h1>
        <p class="hero-sub">
          發布、搜尋並安裝社群貢獻的 AI 工具與應用。<br />
          支援 Antigravity、Claude Code、Cursor、Codex 等多種 AI 工具。
        </p>

        <!-- Search -->
        <div class="search-wrap">
          <input
            v-model="query"
            type="text"
            placeholder="搜尋 Skills…（例如：web-search、code-review）"
            class="search-input"
            @keyup.enter="doSearch"
            id="hero-search"
          />
          <button class="btn-primary search-btn" @click="doSearch">搜尋</button>
        </div>

        <div class="install-hint">
          <span class="code-inline">pip install agentskills</span>
          <span class="text-muted">然後執行</span>
          <span class="code-inline">agentskills search &lt;keyword&gt;</span>
        </div>
      </div>
    </section>

    <!-- ── Stats ── -->
    <section class="stats-bar">
      <div class="stats-inner">
        <div class="stat-item">
          <span class="stat-num">{{ store.stats.total_skills }}</span>
          <span class="stat-label">Skills</span>
        </div>
        <div class="stat-divider" />
        <div class="stat-item">
          <span class="stat-num">{{ store.stats.total_downloads }}</span>
          <span class="stat-label">下載次數</span>
        </div>
        <div class="stat-divider" />
        <div class="stat-item">
          <span class="stat-num">{{ AGENTS.length }}</span>
          <span class="stat-label">支援的 Agents</span>
        </div>
      </div>
    </section>

    <!-- ── Hot Tags ── -->
    <section v-if="store.tags && store.tags.length > 0" class="section">
      <div class="section-inner">
        <h2 class="section-title">熱門標籤</h2>
        <div class="tags-cloud">
          <span
            v-for="t in store.tags.slice(0, 16)"
            :key="t.tag"
            class="tag tag-lg"
            @click="searchByTag(t.tag)"
          >
            {{ t.tag }}
            <span class="tag-count">{{ t.count }}</span>
          </span>
        </div>
      </div>
    </section>

    <!-- ── Featured Skills ── -->
    <section class="section">
      <div class="section-inner">
        <div class="section-header">
          <h2 class="section-title">精選 Skills</h2>
          <RouterLink to="/skills" class="view-all">全部 →</RouterLink>
        </div>

        <div v-if="store.loading" class="skills-grid">
          <div v-for="i in 6" :key="i" class="skill-skeleton">
            <div class="skeleton" style="height:40px;width:40px;border-radius:10px;" />
            <div style="flex:1;display:flex;flex-direction:column;gap:8px;">
              <div class="skeleton" style="height:16px;width:60%;" />
              <div class="skeleton" style="height:12px;width:40%;" />
            </div>
          </div>
        </div>

        <div v-else class="skills-grid">
          <SkillCard
            v-for="(skill, i) in store.skills.slice(0, 6)"
            :key="skill.name"
            :skill="skill"
            :style="{ animationDelay: `${i * 60}ms` }"
            class="fade-up"
          />
        </div>
      </div>
    </section>

    <!-- ── Featured MCP Servers ── -->
    <section class="section mcp-featured-section">
      <div class="section-inner">
        <div class="section-header">
          <h2 class="section-title">🔌 精選 MCP Servers</h2>
          <RouterLink to="/mcp" class="view-all mcp-view-all">全部 →</RouterLink>
        </div>

        <div v-if="mcpLoading" class="mcp-grid">
          <div v-for="i in 4" :key="i" class="mcp-skeleton">
            <div class="skeleton" style="height:40px;width:40px;border-radius:10px;" />
            <div style="flex:1;display:flex;flex-direction:column;gap:8px;">
              <div class="skeleton" style="height:16px;width:55%;" />
              <div class="skeleton" style="height:12px;width:35%;" />
            </div>
          </div>
        </div>

        <div v-else-if="featuredMcps.length === 0" class="mcp-empty">
          <span class="mcp-empty-icon">🔌</span>
          <span>尚未發布任何 MCP Server</span>
        </div>

        <div v-else class="mcp-grid">
          <McpCard
            v-for="(mcp, i) in featuredMcps"
            :key="mcp.name"
            :mcp="mcp"
            :style="{ animationDelay: `${i * 60}ms` }"
            class="fade-up"
          />
        </div>
      </div>
    </section>

    <!-- ── Agents Support ── -->
    <section class="section agents-section">
      <div class="section-inner">
        <h2 class="section-title">🤖 支援的 Agents</h2>
        <div class="agents-table-wrap">
          <table class="agents-table">
            <thead>
              <tr>
                <th>Agent</th>
                <th>識別名稱</th>
                <th>全域技能目錄</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="a in AGENTS" :key="a.id">
                <td><strong>{{ a.name }}</strong></td>
                <td><code>{{ a.id }}</code></td>
                <td><code>{{ a.dir }}</code></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- ── Quick Start ── -->
    <section class="section quickstart-section">
      <div class="section-inner">
        <h2 class="section-title">⚡ 快速開始</h2>
        <div class="quickstart-grid">
          <div class="qs-card card">
            <div class="qs-num">01</div>
            <h3>安裝 CLI</h3>
            <div class="code-block">pip install agentskills</div>
          </div>
          <div class="qs-card card">
            <div class="qs-num">02</div>
            <h3>搜尋 Skill</h3>
            <div class="code-block">agentskills search web-search</div>
          </div>
          <div class="qs-card card">
            <div class="qs-num">03</div>
            <h3>安裝 Skill</h3>
            <div class="code-block">agentskills pull web-search{{ '\n' }}# 或指定 Agent{{ '\n' }}agentskills pull web-search --agent cursor</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSkillsStore } from '@/stores/skills'
import { mcpApi } from '@/api'
import SkillCard from '@/components/SkillCard.vue'
import McpCard from '@/components/McpCard.vue'

const router = useRouter()
const store = useSkillsStore()
const query = ref('')
const featuredMcps = ref([])
const mcpLoading = ref(true)

const AGENTS = [
  { name: 'Antigravity',    id: 'antigravity',    dir: '~/.gemini/antigravity/skills/' },
  { name: 'Claude Code',    id: 'claude-code',    dir: '~/.claude/skills/' },
  { name: 'Claude Desktop', id: 'claude-desktop', dir: '~/.config/claude/skills/' },
  { name: 'Cursor',         id: 'cursor',         dir: '.cursor/skills/' },
  { name: 'Codex',          id: 'codex',          dir: '.codex/skills/' },
  { name: 'Gemini',         id: 'gemini',         dir: '~/.gemini/skills/' },
  { name: 'Kiro',           id: 'kiro',           dir: '~/.kiro/skills/' },
  { name: 'OpenCode',       id: 'opencode',       dir: '.opencode/skills/' },
  { name: 'GitHub Copilot', id: 'github-copilot', dir: '.github/copilot/skills/' },
  { name: 'Roo Code',       id: 'roo',            dir: '.roo/skills/' },
]

function doSearch() {
  if (!query.value.trim()) {
    router.push('/skills')
  } else {
    router.push({ path: '/skills', query: { q: query.value.trim() } })
  }
}

function searchByTag(tag) {
  router.push({ path: '/skills', query: { tags: tag } })
}

onMounted(() => {
  store.fetchSkills({ sort: 'downloads' })
  store.fetchTags()
  store.fetchStats()
  // 載入精選 MCP
  mcpApi.list({ sort: 'installs', per_page: 4 })
    .then(res => { featuredMcps.value = res.data?.mcps || res.data?.items || [] })
    .catch(() => {})
    .finally(() => { mcpLoading.value = false })
})
</script>

<style scoped>
/* Hero */
.hero {
  padding: 6rem 1.5rem 4rem;
  text-align: center;
  background: radial-gradient(ellipse 80% 60% at 50% -10%, rgba(37,164,100,0.14) 0%, transparent 70%);
}
.hero-inner { max-width: 720px; margin: 0 auto; }
.hero-badge {
  display: inline-flex;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
  border: 1px solid rgba(37,164,100,0.35);
  color: var(--accent);
  background: var(--accent-dim);
  margin-bottom: 1.5rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.hero-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: clamp(2rem, 5vw, 3.2rem);
  font-weight: 700;
  line-height: 1.2;
  margin: 0 0 1.25rem;
}
.hero-accent { color: var(--accent); }
.hero-sub { color: var(--text-secondary); font-size: 1.05rem; line-height: 1.7; margin-bottom: 2.5rem; }

/* Search */
.search-wrap {
  display: flex;
  gap: 0.75rem;
  max-width: 600px;
  margin: 0 auto 1.25rem;
}
.search-input {
  flex: 1;
  padding: 0.75rem 1.2rem;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 0.95rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-dim);
}
.search-input::placeholder { color: var(--text-muted); }
.search-btn { min-width: 80px; }
.install-hint {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  justify-content: center;
  flex-wrap: wrap;
  font-size: 0.85rem;
}
.code-inline {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 5px;
  padding: 2px 8px;
  color: var(--accent);
}
.text-muted { color: var(--text-muted); }

/* Stats */
.stats-bar {
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-secondary);
}
.stats-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3rem;
}
.stat-item { text-align: center; }
.stat-num {
  display: block;
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
}
.stat-label { font-size: 0.8rem; color: var(--text-muted); }
.stat-divider { width: 1px; height: 40px; background: var(--border); }

/* Sections */
.section { padding: 3.5rem 1.5rem; }
.section-inner { max-width: 1200px; margin: 0 auto; }
.section-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.35rem;
  font-weight: 700;
  margin: 0 0 1.5rem;
}
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; }
.view-all { font-size: 0.88rem; color: var(--accent); }

/* Tags cloud */
.tags-cloud { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.tag-lg { font-size: 0.82rem; padding: 4px 12px; }
.tag-count {
  margin-left: 4px;
  font-size: 0.7em;
  background: rgba(255,255,255,0.1);
  border-radius: 10px;
  padding: 0 5px;
}

/* Skills grid */
.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}
.skill-skeleton {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.25rem;
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}

/* MCP Featured */
.mcp-featured-section { padding-top: 0; }
.mcp-view-all { color: #f97316; }
.mcp-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}
.mcp-skeleton {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.25rem;
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
}
.mcp-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 3rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}
.mcp-empty-icon { font-size: 2rem; }

/* Agents table */
.agents-section { background: var(--bg-secondary); border-top: 1px solid var(--border-subtle); border-bottom: 1px solid var(--border-subtle); }
.agents-table-wrap { overflow-x: auto; }
.agents-table { width: 100%; border-collapse: collapse; }
.agents-table th, .agents-table td {
  padding: 0.75rem 1rem;
  border: 1px solid var(--border-subtle);
  font-size: 0.88rem;
  text-align: left;
}
.agents-table th { background: var(--bg-card); color: var(--text-secondary); font-weight: 600; }
.agents-table td code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: var(--accent);
  background: var(--accent-dim);
  padding: 1px 6px;
  border-radius: 4px;
}

/* Quick start */
.quickstart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
.qs-card { padding: 1.5rem; display: flex; flex-direction: column; gap: 0.6rem; }
.qs-num {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent);
  opacity: 0.5;
  line-height: 1;
}
.qs-card h3 { font-size: 1rem; font-weight: 600; margin: 0; }
</style>
