<template>
  <div class="browse">
    <div class="browse-inner">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="filter-group">
          <label class="filter-label">搜尋</label>
          <input v-model="q" class="filter-input" placeholder="關鍵字…" id="browse-search" @input="debouncedSearch" />
        </div>

        <div class="filter-group">
          <label class="filter-label">排序</label>
          <select v-model="sort" class="filter-input" @change="doSearch">
            <option value="downloads">最多下載</option>
            <option value="created_at">最新發布</option>
            <option value="name">名稱</option>
          </select>
        </div>

        <!-- 分類（從後端讀取 category） -->
        <div class="filter-group">
          <label class="filter-label">分類</label>
          <nav class="category-nav">
            <button
              v-for="cat in CATEGORIES"
              :key="cat.id"
              class="cat-btn"
              :class="{ active: selectedCategory === cat.id }"
              @click="selectCategory(cat.id)"
            >
              <span class="cat-icon">{{ cat.icon }}</span>
              <span class="cat-name">{{ cat.label }}</span>
              <span v-if="categoryCounts[cat.id] !== undefined" class="cat-count">
                {{ categoryCounts[cat.id] }}
              </span>
            </button>
          </nav>
        </div>

        <!-- 熱門標籤 -->
        <div v-if="store.tags.length" class="filter-group">
          <label class="filter-label">熱門標籤</label>
          <div class="tags-list">
            <span
              v-for="t in store.tags.slice(0, 15)"
              :key="t.tag"
              class="tag"
              :class="{ active: selectedTag === t.tag }"
              @click="toggleTag(t.tag)"
            >
              {{ t.tag }} <span class="tag-count">{{ t.count }}</span>
            </span>
          </div>
        </div>
      </aside>

      <!-- Main -->
      <main class="browse-main">
        <div class="browse-header">
          <h1 class="browse-title">
            {{ store.total }} 個 Skills
            <span v-if="activeLabel" class="filter-indicator">· {{ activeLabel }}</span>
          </h1>
        </div>

        <div v-if="store.loading" class="skills-grid">
          <div v-for="i in 12" :key="i" class="skeleton-card skeleton" style="height:160px" />
        </div>

        <template v-else>
          <div v-if="store.skills.length === 0" class="empty-state">
            <p>😶 找不到符合的 Skills</p>
            <button class="btn-ghost" @click="clearFilters">清除篩選</button>
          </div>
          <div v-else class="skills-grid">
            <SkillCard
              v-for="(skill, i) in store.skills"
              :key="skill.name"
              :skill="skill"
              :style="{ animationDelay: `${i * 40}ms` }"
              class="fade-up"
            />
          </div>

          <!-- Pagination -->
          <div v-if="store.pages > 1" class="pagination">
            <button class="btn-ghost" :disabled="store.page <= 1" @click="changePage(store.page - 1)">← 上一頁</button>
            <span class="page-info">{{ store.page }} / {{ store.pages }}</span>
            <button class="btn-ghost" :disabled="store.page >= store.pages" @click="changePage(store.page + 1)">下一頁 →</button>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSkillsStore } from '@/stores/skills'
import SkillCard from '@/components/SkillCard.vue'

const route = useRoute()
const router = useRouter()
const store = useSkillsStore()

const q = ref(route.query.q || '')
const sort = ref('downloads')
const selectedTag = ref(route.query.tags || '')
const selectedCategory = ref(route.query.category || 'all')

// ── 分類定義（與後端 CATEGORIES 同步）──
const CATEGORIES = [
  { id: 'all',          icon: '🧩', label: '全部' },
  { id: 'coding',       icon: '💻', label: '程式開發' },
  { id: 'web',          icon: '🌐', label: 'Web / UI' },
  { id: 'data',         icon: '📊', label: '資料分析' },
  { id: 'writing',      icon: '✍️',  label: '文案 / 文件' },
  { id: 'ai',           icon: '🤖', label: 'AI / Agent' },
  { id: 'design',       icon: '🎨', label: '設計 / 創作' },
  { id: 'productivity', icon: '⚡', label: '效率工具' },
  { id: 'devops',       icon: '🛠️', label: 'DevOps' },
]

// 從 skills store 的快取計算各分類數量
const categoryCounts = computed(() => {
  const counts = { all: 0 }
  for (const s of store.allSkills || []) {
    counts.all++
    if (s.category) {
      counts[s.category] = (counts[s.category] || 0) + 1
    }
  }
  return counts
})

const activeLabel = computed(() => {
  const parts = []
  if (selectedCategory.value !== 'all') {
    const cat = CATEGORIES.find(c => c.id === selectedCategory.value)
    if (cat) parts.push(cat.label)
  }
  if (q.value) parts.push(`"${q.value}"`)
  if (selectedTag.value) parts.push(`#${selectedTag.value}`)
  return parts.join(' · ')
})

let debounceTimer
function debouncedSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(doSearch, 350)
}

function doSearch() {
  store.page = 1
  syncUrl()
  loadSkills()
}

function selectCategory(id) {
  selectedCategory.value = id
  selectedTag.value = ''
  store.page = 1
  syncUrl()
  loadSkills()
}

function toggleTag(tag) {
  selectedTag.value = selectedTag.value === tag ? '' : tag
  store.page = 1
  loadSkills()
}

function clearFilters() {
  q.value = ''
  selectedTag.value = ''
  selectedCategory.value = 'all'
  sort.value = 'downloads'
  store.page = 1
  syncUrl()
  loadSkills()
}

function changePage(p) {
  store.page = p
  loadSkills()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function loadSkills() {
  store.fetchSkills({
    q: q.value,
    tags: selectedTag.value,
    // 只傳非 all 的分類給後端
    category: selectedCategory.value !== 'all' ? selectedCategory.value : '',
    sort: sort.value,
  })
}

function syncUrl() {
  router.replace({
    query: {
      q: q.value || undefined,
      category: selectedCategory.value !== 'all' ? selectedCategory.value : undefined,
      tags: selectedTag.value || undefined,
    }
  })
}

onMounted(() => {
  store.fetchTags()
  // 一次撈大量（用於計數），儲存在 allSkills
  store.fetchAllForCount()
  loadSkills()
})

watch(sort, loadSkills)
</script>

<style scoped>
.browse { max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem; }
.browse-inner { display: flex; gap: 2rem; align-items: flex-start; }

/* Sidebar */
.sidebar { width: 220px; flex-shrink: 0; position: sticky; top: 80px; }
.filter-group { margin-bottom: 1.75rem; }
.filter-label {
  display: block; font-size: 0.72rem; font-weight: 700;
  color: var(--text-muted); text-transform: uppercase;
  letter-spacing: 0.06em; margin-bottom: 0.6rem;
}
.filter-input {
  width: 100%; padding: 0.5rem 0.75rem;
  background: var(--bg-secondary); border: 1px solid var(--border);
  border-radius: 8px; color: var(--text-primary);
  font-size: 0.875rem; font-family: inherit; outline: none;
}
.filter-input:focus { border-color: var(--accent); }

/* Category Nav */
.category-nav { display: flex; flex-direction: column; gap: 2px; }
.cat-btn {
  display: flex; align-items: center; gap: 0.5rem;
  width: 100%; padding: 0.42rem 0.65rem;
  border-radius: 7px; border: none;
  background: transparent; color: var(--text-muted);
  font-size: 0.85rem; cursor: pointer; text-align: left;
  transition: background 0.13s, color 0.13s;
}
.cat-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }
.cat-btn.active { background: var(--accent-dim); color: var(--accent); font-weight: 600; }
.cat-icon { font-size: 0.95em; flex-shrink: 0; line-height: 1; }
.cat-name { flex: 1; }
.cat-count {
  font-size: 0.72rem; color: var(--text-muted);
  background: rgba(255,255,255,0.07);
  padding: 0 5px; border-radius: 8px;
  min-width: 18px; text-align: center;
}
.cat-btn.active .cat-count { background: rgba(37,164,100,0.15); color: var(--accent); }

/* Tags */
.tags-list { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.tag.active { background: var(--accent-dim); border-color: var(--accent); }
.tag-count { font-size: 0.7em; opacity: 0.7; }

/* Main */
.browse-main { flex: 1; min-width: 0; }
.browse-header { margin-bottom: 1.25rem; }
.browse-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; }
.filter-indicator { color: var(--accent); font-weight: 400; font-size: 0.9rem; margin-left: 0.35rem; }

.skills-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
.skeleton-card { border-radius: 10px; }

.empty-state { text-align: center; padding: 4rem; color: var(--text-muted); font-size: 0.95rem; }
.empty-state p { margin-bottom: 1rem; font-size: 1.05rem; }

.pagination {
  display: flex; align-items: center; justify-content: center;
  gap: 1rem; margin-top: 2.5rem; padding-top: 1.5rem;
  border-top: 1px solid var(--border-subtle);
}
.page-info { color: var(--text-muted); font-size: 0.88rem; }

@media (max-width: 768px) {
  .browse-inner { flex-direction: column; }
  .sidebar { width: 100%; position: static; }
  .category-nav { flex-direction: row; flex-wrap: wrap; }
  .cat-btn { width: auto; }
}
</style>
