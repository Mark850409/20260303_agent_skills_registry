<template>
  <div class="mcp-browse">
    <div class="mcp-browse-inner">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="filter-group">
          <label class="filter-label">搜尋</label>
          <input v-model="searchQuery" class="filter-input" placeholder="搜尋套件..." />
        </div>
      </aside>

      <!-- Main -->
      <main class="browse-main">
        <div class="browse-header header-container">
          <div>
            <h1 class="browse-title">
              {{ packages.length }} 個 NPM 套件
              <span v-if="searchQuery" class="filter-indicator">· "{{ searchQuery }}"</span>
            </h1>
            <p class="browse-sub">Browse and manage NPM packages for AI Skills & Apps.</p>
          </div>
          <div v-if="registryInfo" class="registry-info-box">
            <p class="info-url">Registry URL: <code>{{ registryInfo.external_url.startsWith('http') ? registryInfo.external_url : 'http://' + registryInfo.external_url }}</code></p>
            <p class="info-note">須使用 <code>npm login</code> 才能發布套件。</p>
          </div>
        </div>

        <div v-if="loading" class="skills-grid">
          <div v-for="i in 6" :key="i" class="skeleton-card skeleton" style="height:160px" />
        </div>
        
        <template v-else>
          <div v-if="filteredPackages.length === 0" class="empty-state">
            <template v-if="!searchQuery && packages.length === 0">
              <p>😶 尚無套件</p>
              <p class="empty-sub">目前 NPM Registry 無庫存套件。</p>
              <div class="cmd-box">
                <code>npm set registry {{ registryInfo?.external_url ? (registryInfo.external_url.startsWith('http') ? registryInfo.external_url : 'http://' + registryInfo.external_url) : 'http://localhost:5005/npm/' }}</code>
                <code>npm login</code>
                <code>npm publish</code>
              </div>
            </template>
            <template v-else>
              <p>😶 找不到符合的套件</p>
              <button class="btn-ghost" @click="searchQuery = ''">清除搜尋</button>
            </template>
          </div>
          
          <div v-else class="skills-grid">
            <div v-for="(pkg, i) in filteredPackages" :key="pkg.name" class="repo-card" :style="{ animationDelay: `${i * 40}ms` }">
              <div class="repo-icon">📦</div>
              <div class="repo-info">
                <div class="pkg-header">
                  <h3 class="pkg-name">{{ pkg.name }}</h3>
                  <div class="pkg-badges">
                    <span v-if="pkg.isRegistered" class="badge badge-registered">已註冊</span>
                    <span v-else class="badge badge-unregistered">未註冊 (僅倉庫)</span>
                    <span v-if="pkg.isMissingInRegistry" class="badge badge-missing">缺失實體</span>
                  </div>
                </div>
                <p>{{ pkg.description || 'NPM Package' }}</p>
              </div>
              <div class="repo-action">
                <router-link :to="{ name: 'NpmPackageDetail', params: { name: pkg.name } }" class="btn-primary">
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
const packages = ref([])
const registryInfo = ref(null)
const loading = ref(true)
const searchQuery = ref('')
const error = ref(null)

const fetchCatalog = async () => {
  loading.value = true
  error.value = null
  try {
    // 1. 同時向後端兩處請求
    const promises = [
      axios.get('/api/npm/catalog'), // 實體倉庫中的套件 (回傳名稱清單)
    ]
    
    // 如果是管理員，也讀取資料庫註冊的套件
    if (authStore.isAdmin && authStore.token) {
      promises.push(axios.get('/api/admin/npm-packages', { 
        params: { per_page: 100 },
        headers: { 'Authorization': `Bearer ${authStore.token}` }
      }))
    }

    const results = await Promise.all(promises)
    
    const catalogNames = results[0].data.packages || []
    let dbPackages = []
    
    if (results.length > 1 && results[1]) {
      dbPackages = results[1].data.packages || []
    }

    // 2. 合併資料：以實體倉庫清單為準
    const merged = catalogNames.map(pkgName => {
      const dbMatch = dbPackages.find(p => p.name === pkgName)
      return {
        name: pkgName,
        ...(dbMatch || {}),
        // 標記是否已在資料庫註冊
        isRegistered: !!dbMatch,
        // 如果資料庫沒敘述，預設為空
        description: dbMatch?.description || ''
      }
    })

    // 3. 另外找出「僅存在於資料庫但倉庫沒實體內容」的
    const orphanedDb = dbPackages.filter(dbp => !catalogNames.includes(dbp.name))
    
    packages.value = [
      ...merged,
      ...orphanedDb.map(p => ({ ...p, isRegistered: true, isMissingInRegistry: true }))
    ]
    
  } catch (err) {
    console.error('Fetch NPM packages failed:', err)
    error.value = '無法載入套件清單'
  } finally {
    loading.value = false
  }
}

const fetchInfo = async () => {
    try {
        const response = await axios.get('/api/npm/info')
        registryInfo.value = response.data
    } catch (error) {
        console.error('Failed to fetch info:', error)
    }
}

const filteredPackages = computed(() => {
  if (!searchQuery.value) return packages.value
  return packages.value.filter(pkg => 
    pkg.name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
    (pkg.description && pkg.description.toLowerCase().includes(searchQuery.value.toLowerCase()))
  )
})

onMounted(() => {
  fetchInfo()
  fetchCatalog()
})
</script>

<style scoped>
.mcp-browse { max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem; }
.pkg-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.25rem; }
.pkg-name { margin: 0; }
.pkg-badges { display: flex; gap: 0.5rem; }
.badge { font-size: 0.7rem; padding: 0.1rem 0.4rem; border-radius: 4px; font-weight: 600; text-transform: uppercase; }
.badge-registered { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); }
.badge-unregistered { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.2); }
.badge-missing { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }
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
.repo-icon { font-size: 2.5rem; margin-bottom: 1rem; background: rgba(249, 115, 22, 0.1); width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; border-radius: 14px; }
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
