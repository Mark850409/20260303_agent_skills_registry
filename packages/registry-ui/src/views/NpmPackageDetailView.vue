<template>
  <div class="repo-detail-page">
    <div class="repo-detail-inner">
      <!-- Breadcrumbs -->
      <nav class="breadcrumb">
        <router-link :to="{ name: 'NpmRegistry' }" class="breadcrumb-link">NPM Registry</router-link>
        <span class="breadcrumb-sep">/</span>
        <span class="breadcrumb-current">{{ pkgName }}</span>
      </nav>

      <header class="detail-header">
        <div>
          <h1 class="detail-title">{{ pkgName }}</h1>
          <p class="detail-sub">{{ packageInfo?.description || 'NPM Package Details & Versions' }}</p>
        </div>
        <div class="header-actions">
          <button @click="fetchInfo" class="btn-secondary" :disabled="loading">
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
            <h4>1. 設定 Registry</h4>
            <div class="cmd-row">
              <code>npm set registry {{ registryUrl }}</code>
              <button @click="copyToClipboard(`npm set registry ${registryUrl}`)" class="btn-copy">複製</button>
            </div>
          </div>
          <div class="usage-step mt-4">
            <h4>2. 登入 Registry</h4>
            <div class="cmd-row">
              <code>npm login</code>
              <button @click="copyToClipboard(`npm login`)" class="btn-copy">複製</button>
            </div>
            <p style="font-size: 0.85rem; color: #9ca3af; margin-top: 0.5rem">
              登入時請使用系統提供（或管理員發配）的 <code>htpasswd</code> 帳號密碼。
            </p>
          </div>
          <div class="usage-step mt-4">
            <h4>3. 安裝套件</h4>
            <div class="cmd-row">
              <code>npm install {{ pkgName }}</code>
              <button @click="copyToClipboard(`npm install ${pkgName}`)" class="btn-copy">複製</button>
            </div>
          </div>
          <div class="usage-step mt-4">
            <h4>4. 刪除 / 取消發布</h4>
            <div class="cmd-row">
              <code>npm unpublish {{ pkgName }} --force</code>
              <button @click="copyToClipboard(`npm unpublish ${pkgName} --force`)" class="btn-copy">複製</button>
            </div>
            <p style="font-size: 0.85rem; color: #9ca3af; margin-top: 0.5rem">
              注意：取消發布後將無法再次發布相同版本的套件（依據 NPM 機制）。
            </p>
          </div>
        </div>
      </section>

      <!-- Versions Table -->
      <section class="tags-section">
        <div class="section-title">
          <span class="icon">🏷️</span> 版本列表
        </div>
        
        <div class="tags-container">
          <div v-if="loading" class="loading-state">
            <div class="spinner"></div>
            <p>載入版本中...</p>
          </div>
          
          <table v-else-if="packageInfo?.versions?.length > 0" class="tags-table">
            <thead>
              <tr>
                <th v-if="authStore.isAuthenticated" style="width: 40px; text-align: center;"><input type="checkbox" /></th>
                <th>版本號 (Version)</th>
                <th>描述 (Description)</th>
                <th>發布者 (Author)</th>
                <th>發布時間</th>
                <th v-if="authStore.isAuthenticated" class="text-right">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="v in packageInfo.versions" :key="v.version" class="tag-row">
                <td v-if="authStore.isAuthenticated" style="text-align: center;"><input type="checkbox" /></td>
                <td>
                  <span class="tag-badge">{{ v.version }}</span>
                </td>
                <td class="text-muted text-sm">
                  {{ v.description || '-' }}
                </td>
                <td>
                  <div class="author-cell">{{ v.author || 'Unknown' }}</div>
                </td>
                <td>
                  <div class="time-cell">{{ formatDate(v.time) }}</div>
                </td>
                 <td v-if="authStore.isAuthenticated" class="text-right">
                  <button @click="deleteVersion(v.version)" class="btn-danger">刪除</button>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-else class="empty-state">
            <p>此套件尚無任何版本。</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const authStore = useAuthStore()
const pkgName = route.params.name
const packageInfo = ref(null)
const registryUrl = ref('http://localhost:5005/npm/')
const loading = ref(true)

const fetchInfo = async () => {
    loading.value = true
    try {
        const infoRes = await axios.get('/api/npm/info')
        if (infoRes.data.external_url) {
            registryUrl.value = infoRes.data.external_url
        }

        const response = await axios.get(`/api/npm/${encodeURIComponent(pkgName)}/info`)
        packageInfo.value = response.data
    } catch (error) {
        console.error('Failed to fetch NPM package info:', error)
        if (!packageInfo.value) {
            packageInfo.value = { versions: [] }
        }
    } finally {
        loading.value = false
    }
}

const deleteVersion = async (version) => {
    alert(`依據 NPM 機制建議不要直接從後台刪除特定版本。若您有管理權限，您可以嘗試透過命令列執行：\nnpm --registry ${registryUrl.value} unpublish ${pkgName}@${version} --force`)
}

const copyToClipboard = (text) => {
    if (!text) return
    navigator.clipboard.writeText(text).then(() => {})
}

const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    const d = new Date(dateStr)
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true })
}

onMounted(() => {
    fetchInfo()
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
.author-cell { display: inline-flex; align-items: center; gap: 0.5rem; background: rgba(255,255,255,0.05); padding: 0.3rem 0.6rem; border-radius: 4px; font-size: 0.85rem; color: var(--text-secondary); }

.time-cell { font-size: 0.9rem; color: var(--text-secondary); }
.text-sm { font-size: 0.9rem; }
.text-muted { color: var(--text-muted); }

input[type="checkbox"] { width: 16px; height: 16px; cursor: pointer; accent-color: #3b82f6; }
</style>
