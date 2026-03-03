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

          <!-- Install section -->
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
            <div class="code-block" style="font-size:0.75rem">my-skill/
├── SKILL.md      ← 必填
├── scripts/      ← 選填
├── references/   ← 選填
└── assets/       ← 選填</div>
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

const INSTALL_TABS = [
  { id: 'default',       label: '預設' },
  { id: 'global',        label: '全域' },
  { id: 'cursor',        label: 'Cursor' },
  { id: 'claude-code',   label: 'Claude Code' },
  { id: 'github',        label: 'GitHub URL' },
]

const skillName = computed(() => route.params.name)

const installCmd = computed(() => {
  const name = skillName.value
  const cmds = {
    default:     `agentskills pull ${name}`,
    global:      `agentskills pull ${name} --global`,
    cursor:      `agentskills pull ${name} --agent cursor`,
    'claude-code': `agentskills pull ${name} --agent claude-code`,
    github:      `agentskills pull github:agentskills/${name}`,
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

@media (max-width: 900px) {
  .detail-inner { flex-direction: column; }
  .detail-sidebar { width: 100%; position: static; flex-direction: row; flex-wrap: wrap; }
  .sidebar-card { flex: 1; min-width: 220px; }
}
</style>
