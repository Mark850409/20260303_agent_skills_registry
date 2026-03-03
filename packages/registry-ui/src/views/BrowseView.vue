<template>
  <div class="browse">
    <div class="browse-inner">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="filter-group">
          <label class="filter-label">搜尋</label>
          <input v-model="q" class="filter-input" placeholder="關鍵字…" @input="debouncedSearch" id="browse-search" />
        </div>
        <div class="filter-group">
          <label class="filter-label">排序</label>
          <select v-model="sort" class="filter-input" @change="doSearch">
            <option value="downloads">最多下載</option>
            <option value="created_at">最新發布</option>
            <option value="name">名稱</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">標籤</label>
          <div class="tags-list">
            <span
              v-for="t in store.tags.slice(0, 20)"
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
            <span v-if="q || selectedTag" class="filter-indicator">
              {{ q ? `"${q}"` : '' }}{{ q && selectedTag ? ' · ' : '' }}{{ selectedTag ? `#${selectedTag}` : '' }}
            </span>
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
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSkillsStore } from '@/stores/skills'
import SkillCard from '@/components/SkillCard.vue'

const route = useRoute()
const router = useRouter()
const store = useSkillsStore()

const q = ref(route.query.q || '')
const sort = ref('downloads')
const selectedTag = ref(route.query.tags || '')

let debounceTimer

function debouncedSearch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(doSearch, 350)
}

function doSearch() {
  store.page = 1
  router.replace({ query: { q: q.value || undefined, tags: selectedTag.value || undefined } })
}

function toggleTag(tag) {
  selectedTag.value = selectedTag.value === tag ? '' : tag
  doSearch()
}

function clearFilters() {
  q.value = ''; selectedTag.value = ''; sort.value = 'downloads'
  doSearch()
}

function changePage(p) {
  store.page = p
  loadSkills()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function loadSkills() {
  store.fetchSkills({ q: q.value, tags: selectedTag.value, sort: sort.value })
}

onMounted(() => {
  store.fetchTags()
  loadSkills()
})

watch([sort, q, selectedTag], () => {
  loadSkills()
})
</script>

<style scoped>
.browse { max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem; }
.browse-inner { display: flex; gap: 2rem; align-items: flex-start; }

/* Sidebar */
.sidebar { width: 220px; flex-shrink: 0; position: sticky; top: 80px; }
.filter-group { margin-bottom: 1.5rem; }
.filter-label { display: block; font-size: 0.78rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
.filter-input {
  width: 100%; padding: 0.5rem 0.75rem;
  background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px;
  color: var(--text-primary); font-size: 0.875rem; font-family: inherit; outline: none;
}
.filter-input:focus { border-color: var(--accent); }
.tags-list { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.tag.active { background: var(--accent-dim); border-color: var(--accent); }
.tag-count { font-size: 0.7em; opacity: 0.7; }

/* Main */
.browse-main { flex: 1; min-width: 0; }
.browse-header { margin-bottom: 1.25rem; }
.browse-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; }
.filter-indicator { color: var(--accent); font-weight: 400; font-size: 0.9rem; margin-left: 0.5rem; }

.skills-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
.skeleton-card { border-radius: 10px; }

.empty-state { text-align: center; padding: 4rem; color: var(--text-muted); font-size: 0.95rem; }
.empty-state p { margin-bottom: 1rem; font-size: 1.05rem; }

.pagination { display: flex; align-items: center; justify-content: center; gap: 1rem; margin-top: 2.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border-subtle); }
.page-info { color: var(--text-muted); font-size: 0.88rem; }

@media (max-width: 768px) {
  .browse-inner { flex-direction: column; }
  .sidebar { width: 100%; position: static; }
}
</style>
