<template>
  <div class="mcp-browse">
    <div class="mcp-browse-inner">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="filter-group">
          <label class="filter-label">搜尋</label>
          <input v-model="q" class="filter-input" placeholder="搜尋 MCP…" @input="debouncedSearch" />
        </div>

        <!-- Transport -->
        <div class="filter-group">
          <label class="filter-label">連線方式</label>
          <nav class="cat-nav">
            <button v-for="t in TRANSPORTS" :key="t.id" class="cat-btn" :class="{ active: selectedTransport === t.id }" @click="selectTransport(t.id)">
              <span>{{ t.icon }}</span><span>{{ t.label }}</span>
            </button>
          </nav>
        </div>

        <!-- 分類 -->
        <div class="filter-group">
          <label class="filter-label">分類</label>
          <nav class="cat-nav">
            <button v-for="cat in CATEGORIES" :key="cat.id" class="cat-btn" :class="{ active: selectedCat === cat.id }" @click="selectCat(cat.id)">
              <span class="cat-icon">{{ cat.icon }}</span>
              <span class="cat-name">{{ cat.label }}</span>
              <span v-if="catCounts[cat.id] !== undefined" class="cat-count">{{ catCounts[cat.id] }}</span>
            </button>
          </nav>
        </div>

        <!-- 熱門標籤 -->
        <div v-if="availableTags.length" class="filter-group">
          <label class="filter-label">熱門標籤</label>
          <div class="tags-list">
            <span v-for="t in availableTags.slice(0,15)" :key="t.tag" class="tag" :class="{ active: selectedTag === t.tag }" @click="toggleTag(t.tag)">
              {{ t.tag }} <span class="tag-count">{{ t.count }}</span>
            </span>
          </div>
        </div>
      </aside>

      <!-- Main -->
      <main class="browse-main">
        <div class="browse-header">
          <div>
            <h1 class="browse-title">
              {{ total }} 個 MCP Servers
              <span v-if="activeLabel" class="filter-indicator">· {{ activeLabel }}</span>
            </h1>
            <p class="browse-sub">探索可連接 AI Agent 的 Model Context Protocol 伺服器</p>
          </div>
        </div>

        <div v-if="loading" class="skills-grid">
          <div v-for="i in 12" :key="i" class="skeleton-card skeleton" style="height:160px" />
        </div>
        <template v-else>
          <div v-if="mcps.length === 0" class="empty-state">
            <p>😶 找不到符合的 MCP Servers</p>
            <button class="btn-ghost" @click="clearFilters">清除篩選</button>
          </div>
          <div v-else class="skills-grid">
            <McpCard v-for="(m, i) in mcps" :key="m.name" :mcp="m" :style="{ animationDelay: `${i * 40}ms` }" />
          </div>
          <div v-if="pages > 1" class="pagination">
            <button class="btn-ghost" :disabled="page <= 1" @click="changePage(page-1)">← 上一頁</button>
            <span class="page-info">{{ page }} / {{ pages }}</span>
            <button class="btn-ghost" :disabled="page >= pages" @click="changePage(page+1)">下一頁 →</button>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { mcpApi } from '@/api'
import McpCard from '@/components/McpCard.vue'

const route = useRoute()
const router = useRouter()

const q             = ref(route.query.q || '')
const selectedCat   = ref(route.query.category || 'all')
const selectedTransport = ref(route.query.transport || 'all')
const selectedTag   = ref(route.query.tags || '')
const page          = ref(1)
const pages         = ref(1)
const total         = ref(0)
const mcps          = ref([])
const loading       = ref(false)
const availableTags = ref([])
const allMcps       = ref([])

const TRANSPORTS = [
  { id: 'all',   icon: '📡', label: '全部' },
  { id: 'sse',   icon: '🔗', label: 'Remote SSE' },
  { id: 'stdio', icon: '💻', label: 'Stdio (本地)' },
]

const CATEGORIES = [
  { id: 'all',          icon: '🧩', label: '全部' },
  { id: 'coding',       icon: '💻', label: 'Coding & Dev Tools' },
  { id: 'web',          icon: '🌐', label: 'Web 瀏覽' },
  { id: 'search',       icon: '🔍', label: '網路搜尋' },
  { id: 'data',         icon: '📊', label: 'Data & Analytics' },
  { id: 'database',     icon: '🗄️', label: 'Database & SQL' },
  { id: 'ai',           icon: '🤖', label: 'AI 智能' },
  { id: 'productivity', icon: '⚡', label: 'Productivity' },
  { id: 'writing',      icon: '✍️', label: '文案文件' },
  { id: 'design',       icon: '🎨', label: '設計創作' },
  { id: 'devops',       icon: '🛠️', label: 'Cloud & DevOps' },
  { id: 'communication',icon: '💬', label: 'Communication' },
  { id: 'maps',         icon: '📍', label: 'Maps & Geodata' },
  { id: 'finance',      icon: '💰', label: 'Finance & Crypto' },
  { id: 'science',      icon: '🧪', label: 'Science & Math' },
  { id: 'travel',       icon: '✈️',  label: 'Travel & Lifestyle' },
  { id: 'health',       icon: '🏥', label: 'Health & Fitness' },
  { id: 'other',        icon: '📦', label: '其他' },
]

const catCounts = computed(() => {
  const c = { all: allMcps.value.length }
  for (const m of allMcps.value) {
    if (m.category) c[m.category] = (c[m.category] || 0) + 1
  }
  return c
})

const activeLabel = computed(() => {
  const parts = []
  if (selectedCat.value !== 'all') parts.push(CATEGORIES.find(c=>c.id===selectedCat.value)?.label)
  if (selectedTransport.value !== 'all') parts.push(TRANSPORTS.find(t=>t.id===selectedTransport.value)?.label)
  if (q.value) parts.push(`"${q.value}"`)
  if (selectedTag.value) parts.push(`#${selectedTag.value}`)
  return parts.filter(Boolean).join(' · ')
})

let timer
function debouncedSearch() {
  clearTimeout(timer)
  timer = setTimeout(loadData, 350)
}

function selectCat(id) { selectedCat.value = id; page.value = 1; syncUrl(); loadData() }
function selectTransport(id) { selectedTransport.value = id; page.value = 1; loadData() }
function toggleTag(tag) { selectedTag.value = selectedTag.value === tag ? '' : tag; page.value = 1; loadData() }
function clearFilters() { q.value = ''; selectedCat.value = 'all'; selectedTransport.value = 'all'; selectedTag.value = ''; page.value = 1; syncUrl(); loadData() }
function changePage(p) { page.value = p; loadData(); window.scrollTo({top:0,behavior:'smooth'}) }

function syncUrl() {
  router.replace({ query: {
    q: q.value || undefined,
    category: selectedCat.value !== 'all' ? selectedCat.value : undefined,
    tags: selectedTag.value || undefined,
  }})
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      q: q.value,
      category: selectedCat.value !== 'all' ? selectedCat.value : '',
      transport: selectedTransport.value !== 'all' ? selectedTransport.value : '',
      tags: selectedTag.value,
      page: page.value,
      per_page: 20,
    }
    const res = await mcpApi.list(params)
    mcps.value  = res.data.mcps || []
    total.value = res.data.total || 0
    pages.value = res.data.pages || 1
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadData()
  try {
    const [tagsRes, allRes] = await Promise.all([
      mcpApi.tags(),
      mcpApi.list({ per_page: 500 }),
    ])
    availableTags.value = tagsRes.data || []
    allMcps.value = allRes.data.mcps || []
  } catch {}
})
</script>

<style scoped>
.mcp-browse { max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem; }
.mcp-browse-inner { display: flex; gap: 2rem; align-items: flex-start; }

.sidebar { width: 220px; flex-shrink: 0; position: sticky; top: 80px; }
.filter-group { margin-bottom: 1.75rem; }
.filter-label { display: block; font-size: 0.72rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.6rem; }
.filter-input { width: 100%; padding: 0.5rem 0.75rem; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); font-size: 0.875rem; font-family: inherit; outline: none; }
.filter-input:focus { border-color: #f97316; }

.cat-nav { display: flex; flex-direction: column; gap: 2px; }
.cat-btn { display: flex; align-items: center; gap: 0.5rem; width: 100%; padding: 0.4rem 0.65rem; border-radius: 7px; border: none; background: transparent; color: var(--text-muted); font-size: 0.85rem; cursor: pointer; text-align: left; transition: all 0.12s; }
.cat-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }
.cat-btn.active { background: rgba(249,115,22,0.12); color: #f97316; font-weight: 600; }
.cat-name { flex: 1; }
.cat-count { font-size: 0.7rem; color: var(--text-muted); background: rgba(255,255,255,0.07); padding: 0 5px; border-radius: 8px; min-width: 18px; text-align: center; }
.cat-btn.active .cat-count { background: rgba(249,115,22,0.15); color: #f97316; }

.tags-list { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.tag { font-size: 0.72rem; padding: 2px 7px; border-radius: 10px; border: 1px solid var(--border); background: var(--bg-secondary); color: var(--text-muted); cursor: pointer; transition: all 0.12s; }
.tag:hover { border-color: #f97316; color: #f97316; }
.tag.active { background: rgba(249,115,22,0.12); border-color: #f97316; color: #f97316; }
.tag-count { font-size: 0.68em; opacity: 0.7; }

.browse-main { flex: 1; min-width: 0; }
.browse-header { margin-bottom: 1.25rem; }
.browse-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; margin: 0 0 0.25rem; }
.browse-sub { color: var(--text-muted); font-size: 0.85rem; margin: 0; }
.filter-indicator { color: #f97316; font-weight: 400; font-size: 0.9rem; }

.skills-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
.skeleton-card { border-radius: 10px; }

.empty-state { text-align: center; padding: 4rem; color: var(--text-muted); }
.empty-state p { margin-bottom: 1rem; font-size: 1.05rem; }

.pagination { display: flex; align-items: center; justify-content: center; gap: 1rem; margin-top: 2.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border-subtle); }
.page-info { color: var(--text-muted); font-size: 0.88rem; }

@media (max-width: 768px) {
  .mcp-browse-inner { flex-direction: column; }
  .sidebar { width: 100%; position: static; }
  .cat-nav { flex-direction: row; flex-wrap: wrap; }
  .cat-btn { width: auto; }
}
</style>
