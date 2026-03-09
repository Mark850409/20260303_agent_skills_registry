<template>
  <div class="mcp-browse">
    <div class="mcp-browse-inner">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="filter-group">
          <label class="filter-label">搜尋</label>
          <input v-model="searchQuery" class="filter-input" placeholder="搜尋倉庫..." />
        </div>
      </aside>

      <!-- Main -->
      <main class="browse-main">
        <div class="browse-header header-container">
          <div>
            <h1 class="browse-title">
              {{ repositories.length }} 個 Docker 倉庫
              <span v-if="searchQuery" class="filter-indicator">· "{{ searchQuery }}"</span>
            </h1>
            <p class="browse-sub">Browse and manage Docker container images for AI Skills & Apps.</p>
          </div>
          <div v-if="registryInfo" class="registry-info-box">
            <p class="info-url">Registry URL: <code>{{ registryInfo.external_url || 'localhost:5005' }}</code></p>
            <p class="info-note">須使用 <code>docker login</code> 才能推送鏡像。</p>
          </div>
        </div>

        <div v-if="loading" class="skills-grid">
          <div v-for="i in 6" :key="i" class="skeleton-card skeleton" style="height:160px" />
        </div>
        
        <template v-else>
          <div v-if="filteredRepositories.length === 0" class="empty-state">
            <template v-if="!searchQuery && repositories.length === 0">
              <p>😶 尚無倉庫</p>
              <p class="empty-sub">請先到系統後台新增 Docker 倉庫，再進行鏡像推送。</p>
              <div class="cmd-box">
                <code>docker login {{ registryInfo?.external_url || 'localhost:5005' }}</code>
                <code>docker tag my-image {{ registryInfo?.external_url || 'localhost:5005' }}/&lt;your-repo&gt;:latest</code>
                <code>docker push {{ registryInfo?.external_url || 'localhost:5005' }}/&lt;your-repo&gt;:latest</code>
              </div>
            </template>
            <template v-else>
              <p>😶 找不到符合的倉庫</p>
              <button class="btn-ghost" @click="searchQuery = ''">清除搜尋</button>
            </template>
          </div>
          
          <div v-else class="skills-grid">
            <div v-for="(repo, i) in filteredRepositories" :key="repo.name" class="repo-card pointer" @click="goToRepo(repo.name)" :style="{ animationDelay: `${i * 40}ms` }">
              <div class="repo-icon">📦</div>
              <div class="repo-info">
                <h3 class="repo-name">{{ repo.name }}</h3>
                <p v-if="repo.description" class="repo-desc">{{ repo.description }}</p>
                <p v-else class="repo-desc text-muted italic">無描述</p>
              </div>
              <div class="repo-action">
                <router-link :to="{ name: 'DockerRepoDetail', params: { repo: repo.name } }" class="btn-primary">
                  查看詳情 →
                </router-link>
              </div>
            </div>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const repositories = ref([])
const registryInfo = ref(null)
const loading = ref(true)
const searchQuery = ref('')

const fetchCatalog = async () => {
  try {
    // 取得資料庫中倉庫資訊
    let response = null
    if (authStore.token) {
      response = await axios.get('/api/admin/docker-repos?per_page=100', {
         headers: { 'Authorization': `Bearer ${authStore.token}` }
      }).catch(() => null)
    }
    
    if (response && response.data && response.data.repositories) {
         repositories.value = response.data.repositories.map(r => ({
             name: r.name,
             description: r.description
         }))
    } else {
        // Fallback or user without admin permission
        const catRes = await axios.get('/api/docker/catalog')
        repositories.value = (catRes.data.repositories || []).map(r => ({ 
            name: typeof r === 'string' ? r : r.name, 
            description: typeof r === 'string' ? '' : (r.description || '') 
        }))
    }

  } catch (error) {
    console.error('Failed to fetch catalog:', error)
  } finally {
    loading.value = false
  }
}

const fetchInfo = async () => {
    try {
        const response = await axios.get('/api/docker/info')
        registryInfo.value = response.data
    } catch (error) {
        console.error('Failed to fetch info:', error)
    }
}

const filteredRepositories = computed(() => {
  if (!searchQuery.value) return repositories.value
  return repositories.value.filter(repo => 
    repo.name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
    (repo.description && repo.description.toLowerCase().includes(searchQuery.value.toLowerCase()))
  )
})

onMounted(() => {
  fetchInfo()
  fetchCatalog()
})
</script>

<style scoped>
.mcp-browse { max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem; }
.mcp-browse-inner { display: flex; gap: 2rem; align-items: flex-start; }

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
.filter-input:focus { border-color: #f97316; }

/* Main */
.browse-main { flex: 1; min-width: 0; }
.browse-header { margin-bottom: 2rem; }
.header-container { display: flex; justify-content: space-between; align-items: flex-start; }
.browse-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; font-weight: 700; margin: 0 0 0.5rem; color: var(--text-primary); }
.browse-sub { color: var(--text-muted); font-size: 0.95rem; margin: 0; }
.filter-indicator { color: #f97316; font-weight: 400; font-size: 0.9rem; margin-left: 0.35rem; }

.registry-info-box { background: rgba(59, 130, 246, 0.05); border: 1px solid rgba(59, 130, 246, 0.2); padding: 1rem 1.5rem; border-radius: 8px; text-align: right; }
.info-url { font-size: 0.95rem; font-weight: 500; color: #60a5fa; margin: 0 0 0.5rem 0; }
.info-url code { background: rgba(0,0,0,0.3); padding: 0.2rem 0.5rem; border-radius: 4px; font-family: monospace; }
.info-note { font-size: 0.85rem; color: rgba(96, 165, 250, 0.7); margin: 0; }

.skills-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; }
.skeleton-card { border-radius: 12px; background: var(--bg-secondary); animation: pulse 1.5s infinite; }

.repo-card { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; display: flex; flex-direction: column; transition: all 0.2s ease; animation: fadeUp 0.4s ease forwards; opacity: 0; transform: translateY(10px); }
.repo-card:hover { border-color: rgba(255,255,255,0.15); transform: translateY(-3px); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
.repo-icon { font-size: 2.5rem; margin-bottom: 1rem; background: rgba(59, 130, 246, 0.1); width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; border-radius: 14px; }
.repo-info h3 { margin: 0 0 0.4rem 0; font-size: 1.2rem; font-weight: 600; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.repo-info p { margin: 0; font-size: 0.9rem; color: var(--text-muted); }
.repo-action { margin-top: 1.5rem; display: flex; justify-content: flex-end; }
.btn-primary { background: #f97316; color: white; padding: 0.5rem 1.2rem; border-radius: 8px; text-decoration: none; font-size: 0.9rem; font-weight: 500; transition: background 0.2s; }
.btn-primary:hover { background: #ea580c; }
.btn-ghost { background: transparent; border: 1px solid var(--border); color: var(--text-primary); padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer; text-decoration: none; font-size: 0.9rem; transition: background 0.2s; margin-top: 1rem; }
.btn-ghost:hover { background: var(--bg-secondary); }

.empty-state { text-align: center; padding: 5rem 2rem; color: var(--text-muted); background: var(--bg-secondary); border: 1px dashed var(--border); border-radius: 12px; }
.empty-state p { font-size: 1.1rem; margin-bottom: 0.5rem; }
.empty-sub { margin-bottom: 2rem; font-size: 0.95rem; }
.cmd-box { text-align: left; background: rgba(0,0,0,0.4); padding: 1.5rem; border-radius: 8px; display: inline-flex; flex-direction: column; gap: 0.75rem; border: 1px solid rgba(255,255,255,0.05); }
.cmd-box code { color: #9ca3af; font-size: 0.9rem; font-family: monospace; }

@media (max-width: 768px) {
  .mcp-browse-inner { flex-direction: column; }
  .sidebar { width: 100%; position: static; }
  .header-container { flex-direction: column; gap: 1rem; }
  .registry-info-box { text-align: left; width: 100%; box-sizing: border-box; }
}

@keyframes fadeUp {
  to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
