<template>
  <div class="repo-detail-page">
    <div class="repo-detail-inner">
      <!-- Breadcrumbs -->
      <nav class="breadcrumb">
        <router-link :to="{ name: 'DockerRegistry' }" class="breadcrumb-link">Docker Registry</router-link>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-current">{{ repo }}</span>
      </nav>

      <header class="detail-header">
        <div>
          <h1 class="detail-title">{{ repo }}</h1>
          <p class="detail-sub">{{ repoDetails?.description || 'Repository Details & Tags' }}</p>
        </div>
        <div class="header-actions">
          <button @click="fetchTags" class="btn-secondary" :disabled="loading">
            <span v-if="loading" class="spin-icon">↻</span>
            <span v-else>↻</span> 重新整理
          </button>
        </div>
      </header>

      <!-- Usage Snippets -->
      <section class="usage-section">
        <div class="section-title">
          <span class="icon">💻</span> 指令範例
        </div>
        <div class="usage-content">
          <div class="usage-step">
            <h4>1. 登入 Registry</h4>
            <div class="cmd-row">
              <code>docker login {{ registryInfo?.external_url || 'localhost:5005' }}</code>
              <button @click="copyToClipboard(`docker login ${registryInfo?.external_url || 'localhost:5005'}`)" class="btn-copy">複製</button>
            </div>
          </div>
          <div class="usage-step mt-4">
            <h4>2. 標記與推送</h4>
            <div class="cmd-row mb-2">
              <code>docker tag my-image {{ registryInfo?.external_url || 'localhost:5005' }}/{{ repo }}:latest</code>
              <button @click="copyToClipboard(`docker tag my-image ${registryInfo?.external_url || 'localhost:5005'}/${repo}:latest`)" class="btn-copy">複製</button>
            </div>
            <div class="cmd-row">
              <code>docker push {{ registryInfo?.external_url || 'localhost:5005' }}/{{ repo }}:latest</code>
              <button @click="copyToClipboard(`docker push ${registryInfo?.external_url || 'localhost:5005'}/${repo}:latest`)" class="btn-copy">複製</button>
            </div>
          </div>
          <div class="usage-step mt-4">
            <h4>3. 刪除遠端標籤</h4>
            <div class="cmd-row">
              <code>docker rmi {{ registryInfo?.external_url || 'localhost:5005' }}/{{ repo }}:&lt;tag&gt;</code>
              <button @click="copyToClipboard(`docker rmi ${registryInfo?.external_url || 'localhost:5005'}/${repo}:latest`)" class="btn-copy">複製</button>
            </div>
            <p style="font-size: 0.85rem; color: #9ca3af; margin-top: 0.5rem">
              若要徹底刪除伺服器儲存體空間，請聯絡管理員執行 GC 或透過背景管理介面刪除 Manifest。
            </p>
          </div>
        </div>
      </section>

      <!-- Tags Table -->
      <section class="tags-section">
        <div class="section-title">
          <span class="icon">🏷️</span> 標籤列表
        </div>
        
        <div class="tags-container">
          <div class="table-actions" v-if="authStore.isAuthenticated && selectedTags.length > 0" style="padding: 1rem; border-bottom: 1px solid var(--border-subtle); background: rgba(239, 68, 68, 0.05);">
            <span style="margin-right: 1rem; font-size: 0.95rem;">已選擇 {{ selectedTags.length }} 項</span>
            <button @click="deleteSelected" class="btn-danger">批次刪除</button>
          </div>

          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>載入標籤中...</p>
          </div>
          
          <table v-else-if="tags.length > 0" class="tags-table">
            <thead>
              <tr>
                 <th v-if="authStore.isAuthenticated" style="width: 40px; text-align: center;"><input type="checkbox" v-model="selectAll" /></th>
                <th>版本標籤 (Tag)</th>
                <th>Artifact Digest</th>
                <th style="text-align: center;">已簽署</th>
                <th>大小</th>
                <th>安全性漏洞</th>
                <th>SBOM</th>
                <th>最後推送時間</th>
                 <th v-if="authStore.isAuthenticated" class="text-right">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="t in tags" :key="t.tag" class="tag-row">
                 <td v-if="authStore.isAuthenticated" style="text-align: center;"><input type="checkbox" :value="t.tag" v-model="selectedTags" /></td>
                <td>
                  <span class="tag-badge">{{ t.tag }}</span>
                </td>
                <td>
                  <div class="artifact-cell">
                    <span class="icon" style="opacity:0.7">☁️</span>
                    <span class="artifact-sha">{{ t.digest ? t.digest.substring(0, 15) + '...' : 'unknown' }}</span>
                    <button class="btn-copy-small" @click="copyToClipboard(t.digest)" title="複製 Digest">📋</button>
                  </div>
                </td>
                <td style="text-align: center; color: #ef4444;" title="未簽署">
                  <span>⊗</span>
                </td>
                <td class="font-mono">{{ formatSize(t.size) }}</td>
                <td class="text-muted text-sm">不支援掃描</td>
                <td class="text-muted text-sm">-</td>
                <td>
                  <div class="time-cell">{{ formatDate(t.created_at) }}</div>
                </td>
                 <td v-if="authStore.isAuthenticated" class="text-right">
                  <button @click="deleteTag(t.tag)" class="btn-danger">刪除</button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-else class="empty-state">
            <p>此倉庫尚無標籤。</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const authStore = useAuthStore()
const repo = route.params.repo
const tags = ref([])
const selectedTags = ref([])
const registryInfo = ref(null)
const repoDetails = ref(null)
const loading = ref(true)

const selectAll = computed({
  get: () => tags.value.length > 0 && selectedTags.value.length === tags.value.length,
  set: (val) => {
    if (val) {
      selectedTags.value = tags.value.map(t => t.tag)
    } else {
      selectedTags.value = []
    }
  }
})

const fetchTags = async () => {
    loading.value = true
    try {
        const response = await axios.get(`/api/docker/${repo}/tags/details`, {
            headers: { 'Authorization': `Bearer ${authStore.token}` }
        })
        tags.value = response.data.tags || []
    } catch (error) {
        console.error('Failed to fetch tags:', error)
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

const fetchRepoDetails = async () => {
    try {
        if (!authStore.token) return // Skip admin fetch if not logged in
        
        // Because /api/docker/{repo} doesn't expose description right now,
        // we try to fetch it from the admin API. In a real environment, 
        // there should be a public endpoint to get repository metadata.
        // We'll use the admin API as a workaround for now.
        const response = await axios.get(`/api/admin/docker-repos?q=${repo}`, {
            headers: { 'Authorization': `Bearer ${authStore.token}` }
        }).catch(() => null)
        
        if (response && response.data && response.data.repositories) {
            const found = response.data.repositories.find(r => r.name === repo)
            if (found) {
                repoDetails.value = found
            }
        }
    } catch (error) {
        // Silently fail if no permission or not found
    }
}

const deleteTag = async (tag) => {
    if (!confirm(`確定要刪除標籤 ${tag} 嗎？`)) return
    
    try {
        // First get the digest
        const manifestRes = await axios.get(`/api/docker/${repo}/manifest/${tag}`, {
            headers: { 'Authorization': `Bearer ${authStore.token}` }
        })
        const digest = manifestRes.data.digest
        
        if (!digest) {
            alert('無法獲取 Digest，無法刪除。')
            return
        }
        
        await axios.delete(`/api/docker/${repo}/manifest/${digest}`, {
            headers: { 'Authorization': `Bearer ${authStore.token}` }
        })
        alert('刪除成功')
        // Remove from selection if exists
        selectedTags.value = selectedTags.value.filter(t => t !== tag)
        fetchTags()
    } catch (error) {
        console.error('Failed to delete tag:', error)
        alert('刪除失敗: ' + (error.response?.data?.error || error.message))
    }
}

const deleteSelected = async () => {
    if (selectedTags.value.length === 0) return
    if (!confirm(`確定要刪除選取的 ${selectedTags.value.length} 個標籤嗎？`)) return
    
    let successCount = 0
    let failCount = 0
    let lastError = null
    
    for (const tag of selectedTags.value) {
        try {
            const manifestRes = await axios.get(`/api/docker/${repo}/manifest/${tag}`, {
                headers: { 'Authorization': `Bearer ${authStore.token}` }
            })
            const digest = manifestRes.data.digest
            
            if (digest) {
                await axios.delete(`/api/docker/${repo}/manifest/${digest}`, {
                    headers: { 'Authorization': `Bearer ${authStore.token}` }
                })
                successCount++
            } else {
                failCount++
            }
        } catch (error) {
            console.error(`Failed to delete tag ${tag}:`, error)
            failCount++
            lastError = error.response?.data?.error || error.message
        }
    }
    
    if (failCount > 0) {
        alert(`批次刪除完成：成功 ${successCount} 個，失敗 ${failCount} 個。\n最後錯誤：${lastError}`)
    } else {
        alert(`成功刪除 ${successCount} 個標籤`)
    }
    selectedTags.value = []
    fetchTags()
}

const copyToClipboard = (text) => {
    if (!text) return
    navigator.clipboard.writeText(text).then(() => {})
}

const formatSize = (bytes) => {
    if (!bytes) return '-'
    const k = 1024
    const sizes = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    const d = new Date(dateStr)
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true })
}

onMounted(() => {
    fetchInfo()
    fetchRepoDetails()
    fetchTags()
})
</script>

<style scoped>
.repo-detail-page { max-width: 1200px; margin: 0 auto; padding: 2rem 1.5rem; }
.repo-detail-inner { display: flex; flex-direction: column; gap: 2rem; }

.breadcrumb { display: flex; align-items: center; gap: 0.5rem; font-size: 0.95rem; color: var(--text-muted); margin-bottom: 0.5rem; }
.breadcrumb-link { color: var(--text-muted); text-decoration: none; transition: color 0.2s; }
.breadcrumb-link:hover { color: var(--text-primary); }
.breadcrumb-sep { font-size: 0.8rem; opacity: 0.5; }
.breadcrumb-current { color: var(--text-primary); font-weight: 500; }

.detail-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-subtle); padding-bottom: 1.5rem; }
.detail-title { font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 700; margin: 0 0 0.5rem; color: var(--text-primary); }
.detail-sub { color: var(--text-muted); font-size: 1.1rem; margin: 0; }

.btn-secondary { background: var(--bg-secondary); border: 1px solid var(--border); color: var(--text-primary); padding: 0.6rem 1.2rem; border-radius: 8px; font-size: 0.95rem; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 0.5rem; }
.btn-secondary:hover:not(:disabled) { background: var(--border); }
.btn-secondary:disabled { opacity: 0.6; cursor: not-allowed; }

.spin-icon { display: inline-block; animation: spin 1s linear infinite; }
@keyframes spin { 100% { transform: rotate(360deg); } }

.section-title { font-size: 1.4rem; font-weight: 600; color: var(--text-primary); margin-bottom: 1.25rem; display: flex; align-items: center; gap: 0.5rem; }
.section-title .icon { font-size: 1.1em; }

.usage-section { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; padding: 1.75rem; }
.usage-content { background: rgba(0,0,0,0.2); border-radius: 8px; padding: 1.5rem; }
.usage-step h4 { color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; margin: 0 0 0.75rem 0; font-weight: 600; }
.mt-4 { margin-top: 1.5rem; }
.mb-2 { margin-bottom: 0.5rem; }

.cmd-row { display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.3); padding: 0.85rem 1.2rem; border-radius: 6px; border: 1px solid var(--border-subtle); }
.cmd-row code { color: #93c5fd; font-family: monospace; font-size: 0.95rem; }
.btn-copy { background: transparent; border: 1px solid var(--border); color: var(--text-muted); padding: 0.3rem 0.8rem; border-radius: 6px; font-size: 0.8rem; cursor: pointer; opacity: 0.6; transition: all 0.2s; }
.cmd-row:hover .btn-copy { opacity: 1; }
.btn-copy:hover { color: var(--text-primary); border-color: var(--text-muted); background: rgba(255,255,255,0.05); }

.tags-section { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 12px; padding: 1.75rem; }
.tags-container { border: 1px solid var(--border-subtle); border-radius: 8px; overflow: hidden; background: rgba(0,0,0,0.1); }

.tags-table { width: 100%; border-collapse: collapse; text-align: left; }
.tags-table th { background: rgba(0,0,0,0.2); padding: 1rem 1.25rem; font-size: 0.9rem; color: var(--text-muted); font-weight: 600; border-bottom: 1px solid var(--border-subtle); }
.tags-table td { padding: 1.25rem; border-bottom: 1px solid var(--border-subtle); vertical-align: middle; }
.tag-row:last-child td { border-bottom: none; }
.tag-row { transition: background 0.2s ease; }
.tag-row:hover { background: rgba(255,255,255,0.04); }

.text-right { text-align: right; }
.font-mono { font-family: monospace; font-size: 0.95rem; }

/* Adjusted Tag Badge for clickability/readability */
.tag-badge { 
  background: rgba(59, 130, 246, 0.15); 
  color: #93c5fd; 
  padding: 0.4rem 0.8rem; 
  border-radius: 6px; 
  font-size: 0.95rem; 
  font-weight: 500; 
  border: 1px solid rgba(59, 130, 246, 0.3); 
  display: inline-block;
  cursor: pointer;
  transition: all 0.2s;
}
.tag-badge:hover {
  background: rgba(59, 130, 246, 0.25);
  border-color: rgba(59, 130, 246, 0.5);
}

.btn-danger { background: transparent; border: 1px solid rgba(239, 68, 68, 0.3); color: #ef4444; font-size: 0.9rem; font-weight: 500; cursor: pointer; transition: all 0.2s; padding: 0.5rem 1rem; border-radius: 6px; }
.btn-danger:hover { background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.5); }

.loading-state, .empty-state { padding: 4rem; text-align: center; color: var(--text-muted); font-size: 1.1rem; }
.spinner { width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.1); border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1.5rem; }

.artifact-cell { display: flex; align-items: center; gap: 0.6rem; }
.artifact-sha { font-family: monospace; font-size: 0.95rem; color: #d1d5db; }
.btn-copy-small { background: rgba(255,255,255,0.05); border: 1px solid var(--border-subtle); border-radius: 4px; color: var(--text-muted); cursor: pointer; opacity: 0.7; padding: 4px; transition: all 0.2s; display: flex; align-items: center; justify-content: center; width: 24px; height: 24px;}
.btn-copy-small:hover { opacity: 1; color: var(--text-primary); background: rgba(255,255,255,0.1); border-color: var(--text-secondary); }

.time-cell { font-size: 0.9rem; color: var(--text-secondary); }
.text-sm { font-size: 0.9rem; }
.text-muted { color: var(--text-muted); }

input[type="checkbox"] { width: 16px; height: 16px; cursor: pointer; accent-color: #3b82f6; }
</style>
