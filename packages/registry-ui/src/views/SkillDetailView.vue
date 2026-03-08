<template>
  <div class="detail-page">
    <div v-if="store.loading" class="detail-loading">
      <div class="skeleton" style="height:36px;width:40%;margin-bottom:1rem" />
      <div class="skeleton" style="height:16px;width:70%;margin-bottom:0.5rem" />
      <div class="skeleton" style="height:16px;width:55%" />
    </div>

    <template v-else-if="store.currentSkill">
      <div class="detail-inner">
        <!-- Left: Skill Info -->
        <div class="detail-main">
          <div class="detail-header">
            <div class="detail-icon">{{ getIcon(store.currentSkill.tags) }}</div>
            <div>
              <h1 class="detail-name">{{ store.currentSkill.name }}</h1>
              <p class="detail-meta">
                <span>@{{ store.currentSkill.author }}</span>
                <span class="meta-dot">·</span>
                <span>v{{ store.currentSkill.latest_version }}</span>
                <span class="meta-dot">·</span>
                <span>{{ store.currentSkill.license }}</span>
              </p>
            </div>
          </div>

          <p class="detail-desc">{{ store.currentSkill.description }}</p>

          <div class="detail-tags">
            <span v-for="tag in (store.currentSkill.tags || [])" :key="tag" class="tag">{{ tag }}</span>
          </div>

          <div class="install-section card">
            <h3 class="install-title">📦 安裝指令</h3>
            <div class="install-tabs">
              <button
                v-for="tab in INSTALL_TABS"
                :key="tab.id"
                class="tab-btn"
                :class="{ active: activeTab === tab.id }"
                @click="activeTab = tab.id"
              >{{ tab.label }}</button>
            </div>
            <div class="code-block install-code">{{ installCmd }}</div>
            <button class="copy-btn" @click="copyCmd">{{ copied ? '✓ 已複製' : '複製' }}</button>
          </div>

          <!-- Examples section -->
          <div v-if="store.currentSkill?.examples?.length" class="examples-section">
            <h3 class="section-title">📋 快速複製範例</h3>
            <div v-for="(ex, idx) in store.currentSkill.examples" :key="idx" class="example-card">
              <div class="example-text">{{ ex }}</div>
              <button class="example-copy-btn" @click="copyText(ex, idx)">
                {{ activeCopyIdx === idx ? '✓ 已複製' : '複製' }}
              </button>
            </div>
          </div>

          <!-- SKILL.md Content -->
          <div class="skillmd-section">
            <h2 class="skillmd-title">📄 SKILL.md</h2>
            <div class="prose" v-html="renderedMd" />
          </div>
        </div>

        <!-- Right: Sidebar Info -->
        <aside class="detail-sidebar">
          <div class="sidebar-card card">
            <div class="info-row">
              <span class="info-key">下載次數</span>
              <span class="info-val">⬇ {{ store.currentSkill.downloads }}</span>
            </div>
            <div class="info-row" v-if="store.currentSkill.repository">
              <span class="info-key">儲存庫</span>
              <a :href="store.currentSkill.repository" target="_blank" class="info-link">GitHub ↗</a>
            </div>
            <div class="info-row">
              <span class="info-key">最新版本</span>
              <span class="info-val code">v{{ store.currentSkill.latest_version }}</span>
            </div>
            <div class="info-row" v-if="store.currentSkill.created_at">
              <span class="info-key">發布時間</span>
              <span class="info-val">{{ formatDate(store.currentSkill.created_at) }}</span>
            </div>
          </div>

          <!-- Versions -->
          <div v-if="store.currentSkill.versions?.length > 0" class="sidebar-card card">
            <h4 class="sidebar-title">版本歷史</h4>
            <div v-for="v in store.currentSkill.versions" :key="v.version" class="version-row">
              <code>v{{ v.version }}</code>
              <span class="version-date">{{ formatDate(v.published_at) }}</span>
            </div>
          </div>

          <!-- Skill Bundle Structure -->
          <div class="sidebar-card card">
            <h4 class="sidebar-title">📁 Bundle 結構</h4>
            <div class="bundle-tree">
              <div class="bundle-root">📂 my-skill/</div>
              <div class="bundle-items">
                <div class="bundle-item">
                  <span class="bundle-icon">📄</span>
                  <span class="bundle-name">SKILL.md</span>
                  <span class="bundle-badge required">必填</span>
                </div>
                <div class="bundle-item">
                  <span class="bundle-icon">📁</span>
                  <span class="bundle-name">scripts/</span>
                  <span class="bundle-badge optional">選填</span>
                </div>
                <div class="bundle-item">
                  <span class="bundle-icon">📁</span>
                  <span class="bundle-name">references/</span>
                  <span class="bundle-badge optional">選填</span>
                </div>
                <div class="bundle-item last">
                  <span class="bundle-icon">📁</span>
                  <span class="bundle-name">assets/</span>
                  <span class="bundle-badge optional">選填</span>
                </div>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </template>

    <div v-else class="not-found">
      <h2>找不到 Skill 😶</h2>
      <RouterLink to="/skills" class="btn-primary">回到瀏覽</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useSkillsStore } from '@/stores/skills'
import { marked } from 'marked'

const route = useRoute()
const store = useSkillsStore()

const activeTab = ref('default')
const copied = ref(false)
const activeCopyIdx = ref(-1)

const INSTALL_TABS = [
  { id: 'default',       label: '預設' },
  { id: 'global',        label: '全域' },
  { id: 'cursor',        label: 'Cursor' },
  { id: 'claude-code',   label: 'Claude Code' },
  { id: 'claude-desktop', label: 'Claude Desktop' },
  { id: 'codex',         label: 'Codex' },
  { id: 'gemini',        label: 'Gemini' },
  { id: 'antigravity',   label: 'Antigravity' },
  { id: 'kiro',          label: 'Kiro' },
  { id: 'github',        label: 'GitHub URL' },
]

const skillName = computed(() => route.params.name)

const installCmd = computed(() => {
  const name = skillName.value
  const repo = store.currentSkill?.repository || ''
  
  // 嘗試解析 GitHub user/repo
  let githubShort = `agentskills/${name}`
  if (repo.includes('github.com/')) {
    const parts = repo.split('github.com/')[1].split('/')
    if (parts.length >= 2) {
      githubShort = `${parts[0]}/${parts[1]}`.replace(/\.git$/, '')
    }
  }

  const cmds = {
    default:          `agentskills pull ${name}`,
    global:           `agentskills pull ${name} --global`,
    cursor:           `agentskills pull ${name} --agent cursor`,
    'claude-code':    `agentskills pull ${name} --agent claude-code`,
    'claude-desktop': `agentskills pull ${name} --agent claude-desktop`,
    codex:            `agentskills pull ${name} --agent codex`,
    gemini:           `agentskills pull ${name} --agent gemini`,
    antigravity:      `agentskills pull ${name} --agent antigravity`,
    kiro:             `agentskills pull ${name} --agent kiro`,
    github:           `agentskills pull github:${githubShort}`,
  }
  return cmds[activeTab.value] || cmds.default
})

const renderedMd = computed(() => {
  const md = store.currentSkill?.skill_md || ''
  // Strip YAML frontmatter
  const stripped = md.replace(/^---[\s\S]*?---\n?/, '')
  return marked.parse(stripped)
})

function getIcon(tags = []) {
  const map = { search:'🔍', web:'🌐', code:'💻', review:'🔎', git:'🌿', documentation:'📄', testing:'🧪', productivity:'⚡' }
  for (const t of tags) if (map[t]) return map[t]
  return '🧩'
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('zh-TW', { year:'numeric', month:'short', day:'numeric' })
}

async function copyCmd() {
  await navigator.clipboard.writeText(installCmd.value).catch(() => {})
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

async function copyText(text, idx) {
  await navigator.clipboard.writeText(text).catch(() => {})
  activeCopyIdx.value = idx
  setTimeout(() => { activeCopyIdx.value = -1 }, 2000)
}

onMounted(() => {
  store.fetchSkill(skillName.value)
})
</script>

<style scoped>
.detail-page { max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem; }
.detail-loading { max-width: 800px; padding: 2rem 0; }
.detail-inner { display: flex; gap: 2rem; align-items: flex-start; }
.detail-main { flex: 1; min-width: 0; }
.detail-header { display: flex; gap: 1rem; align-items: flex-start; margin-bottom: 1rem; }
.detail-icon { font-size: 2.5rem; background: var(--accent-dim); border-radius: 14px; width: 64px; height: 64px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.detail-name { font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 700; margin: 0 0 0.3rem; }
.detail-meta { color: var(--text-muted); font-size: 0.88rem; margin: 0; display: flex; gap: 0.5rem; flex-wrap: wrap; }
.meta-dot { color: var(--border); }
.detail-desc { color: var(--text-secondary); font-size: 1rem; line-height: 1.6; margin-bottom: 1rem; }
.detail-tags { display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 1.5rem; }

/* Install */
.install-section { padding: 1.25rem; margin-bottom: 2rem; position: relative; }
.install-title { font-size: 0.95rem; font-weight: 600; margin: 0 0 0.75rem; }
.install-tabs { display: flex; gap: 0.4rem; margin-bottom: 0.75rem; flex-wrap: wrap; }
.tab-btn {
  padding: 4px 12px; border-radius: 6px; font-size: 0.78rem; font-weight: 500;
  border: 1px solid var(--border); background: transparent; color: var(--text-muted); cursor: pointer;
  transition: all 0.15s;
}
.tab-btn.active { border-color: var(--accent); color: var(--accent); background: var(--accent-dim); }
.install-code { margin: 0; }
.copy-btn {
  position: absolute; top: 1rem; right: 1rem;
  padding: 4px 12px; border-radius: 6px; font-size: 0.78rem;
  background: var(--bg-secondary); border: 1px solid var(--border); color: var(--text-secondary);
  cursor: pointer; transition: all 0.15s;
}
.copy-btn:hover { border-color: var(--accent); color: var(--accent); }

/* Examples */
.examples-section { margin-bottom: 2.5rem; }
.section-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 0.5rem; color: var(--text-primary); }
.example-card {
  display: flex; gap: 1rem; align-items: center; padding: 1rem 1.25rem;
  background: var(--bg-secondary); border-radius: 12px; margin-bottom: 0.75rem;
  transition: transform 0.2s, box-shadow 0.2s; border: 1px solid var(--border-subtle);
}
.example-card:hover { border-color: var(--accent-dim); transform: translateY(-1px); }
.example-text { flex: 1; font-size: 0.95rem; line-height: 1.5; color: var(--text-secondary); }
.example-copy-btn {
  padding: 8px 18px; border-radius: 8px; font-size: 0.85rem; font-weight: 600;
  background: #6366f1; color: white; border: none; cursor: pointer;
  transition: all 0.2s; white-space: nowrap; box-shadow: 0 2px 4px rgba(99,102,241,0.2);
}
.example-copy-btn:hover { background: #4f46e5; transform: scale(1.02); }
.example-copy-btn:active { transform: scale(0.98); }

/* Markdown */
.skillmd-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 600; margin: 0 0 1rem; }

/* Sidebar */
.detail-sidebar { width: 260px; flex-shrink: 0; position: sticky; top: 80px; display: flex; flex-direction: column; gap: 1rem; }
.sidebar-card { padding: 1.1rem; }
.sidebar-title { font-size: 0.85rem; font-weight: 600; margin: 0 0 0.75rem; }
.info-row { display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0; border-bottom: 1px solid var(--border-subtle); }
.info-row:last-child { border-bottom: none; }
.info-key { color: var(--text-muted); font-size: 0.8rem; }
.info-val { font-size: 0.82rem; color: var(--text-secondary); }
.info-val.code { font-family: 'JetBrains Mono', monospace; color: var(--accent); }
.info-link { color: var(--accent); font-size: 0.8rem; }
.version-row { display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid var(--border-subtle); }
.version-row code { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: var(--accent); }
.version-date { font-size: 0.75rem; color: var(--text-muted); }

.not-found { text-align: center; padding: 6rem 1rem; }
.not-found h2 { margin-bottom: 1.5rem; color: var(--text-secondary); }

/* Bundle Tree */
.bundle-tree {
  font-size: 0.82rem;
}
.bundle-root {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
  padding: 0.35rem 0.6rem;
  background: var(--bg-secondary);
  border-radius: 6px;
}
.bundle-items {
  border-left: 2px solid var(--border);
  margin-left: 0.8rem;
  padding-left: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.bundle-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.28rem 0.5rem;
  border-radius: 5px;
  transition: background 0.15s;
}
.bundle-item:hover { background: var(--bg-secondary); }
.bundle-item.last { margin-top: 0; }
.bundle-icon { font-size: 0.9em; flex-shrink: 0; }
.bundle-name {
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-secondary);
  flex: 1;
}
.bundle-badge {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 1px 7px;
  border-radius: 10px;
  flex-shrink: 0;
}
.bundle-badge.required {
  background: rgba(37,164,100,0.15);
  color: var(--accent);
  border: 1px solid rgba(37,164,100,0.3);
}
.bundle-badge.optional {
  background: rgba(255,255,255,0.06);
  color: var(--text-muted);
  border: 1px solid var(--border-subtle);
}

@media (max-width: 900px) {
  .detail-inner { flex-direction: column; }
  .detail-sidebar { width: 100%; position: static; flex-direction: row; flex-wrap: wrap; }
  .sidebar-card { flex: 1; min-width: 220px; }
}
</style>
