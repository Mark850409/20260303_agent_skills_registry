<template>
  <div class="admin-page fade-up">
    <header class="admin-header">
      <div class="header-content">
        <h1>管理後台</h1>
        <p class="subtitle">{{ currentTab === 'skills' ? 'Registry 數據營運與管控中心' : '系統帳號與權限核發中心' }}</p>
      </div>
      <div class="stats-cards" v-if="currentTab === 'skills'">
        <div class="stat-card">
          <span class="stat-label">總技能數</span>
          <span class="stat-value">{{ stats.total_skills || 0 }}</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">累積下載</span>
          <span class="stat-value">{{ stats.total_downloads || 0 }}</span>
        </div>
      </div>
    </header>

    <div class="tabs-nav">
      <button :class="{ active: currentTab === 'skills' }" @click="currentTab = 'skills'">技能管理</button>
      <button :class="{ active: currentTab === 'users' }" @click="currentTab = 'users'">使用者管理</button>
    </div>

    <!-- 技能管理頁面 -->
    <div v-if="currentTab === 'skills'" class="admin-content card">
      <div class="toolbar">
        <div class="search-box">
          <span class="icon">🔍</span>
          <input v-model="searchQuery" placeholder="搜尋技能名稱或描述..." @input="debouncedFetch" />
        </div>
        <button class="btn-ghost" @click="fetchData(1)">刷新數據</button>
      </div>

      <div class="table-container">
        <table class="admin-table">
          <thead>
            <tr>
              <th>技能名稱</th>
              <th>作者</th>
              <th>標籤</th>
              <th>下載次數</th>
              <th>最新版本</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="skill in skills" :key="skill.id">
              <td class="skill-name-cell">
                <span class="skill-name">{{ skill.name }}</span>
              </td>
              <td>{{ skill.author }}</td>
              <td>
                <div class="tag-row">
                  <span v-for="tag in (skill.tags || []).slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
                </div>
              </td>
              <td>{{ skill.downloads }}</td>
              <td><code>{{ skill.latest_version }}</code></td>
              <td class="actions">
                <button class="btn-action edit" @click="editSkill(skill)">編輯</button>
                <button class="btn-action delete" @click="confirmDelete(skill)">刪除</button>
              </td>
            </tr>
            <tr v-if="skills.length === 0" class="empty-row">
              <td colspan="6">尚無任何技能數據</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 技能分頁 -->
      <div class="pagination" v-if="skillPagination.pages > 1">
        <button :disabled="skillPagination.page === 1" @click="fetchData(skillPagination.page - 1)">上一頁</button>
        <span class="page-info">第 {{ skillPagination.page }} / {{ skillPagination.pages }} 頁 (共 {{ skillPagination.total }} 筆)</span>
        <button :disabled="skillPagination.page === skillPagination.pages" @click="fetchData(skillPagination.page + 1)">下一頁</button>
      </div>
    </div>

    <!-- 使用者管理頁面 -->
    <div v-else-if="currentTab === 'users'" class="admin-content card">
      <div class="toolbar">
        <div class="search-box">
          <span class="icon">🔍</span>
          <input v-model="userSearchQuery" placeholder="搜尋使用者名稱或 Email..." @input="debouncedFetchUsers" />
        </div>
        <div class="toolbar-actions">
          <button class="btn-primary" @click="createUser">+ 新增使用者</button>
          <button class="btn-ghost" @click="fetchUsers(1)">刷新清單</button>
        </div>
      </div>

      <div class="table-container">
        <table class="admin-table">
          <thead>
            <tr>
              <th>使用者</th>
              <th>Email</th>
              <th>角色</th>
              <th>權限數</th>
              <th>建立於</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td><strong>{{ user.username }}</strong></td>
              <td>{{ user.email }}</td>
              <td>
                <span :class="['role-badge', user.role]">{{ user.role }}</span>
              </td>
              <td>{{ (user.permissions || []).length }}</td>
              <td>{{ new Date(user.created_at).toLocaleDateString() }}</td>
              <td class="actions">
                <button class="btn-action edit" @click="editUser(user)">編輯</button>
                <button class="btn-action delete" @click="deleteUser(user)">刪除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 使用者分頁 -->
      <div class="pagination" v-if="userPagination.pages > 1">
        <button :disabled="userPagination.page === 1" @click="fetchUsers(userPagination.page - 1)">上一頁</button>
        <span class="page-info">第 {{ userPagination.page }} / {{ userPagination.pages }} 頁 (共 {{ userPagination.total }} 筆)</span>
        <button :disabled="userPagination.page === userPagination.pages" @click="fetchUsers(userPagination.page + 1)">下一頁</button>
      </div>
    </div>

    <!-- 技能編輯 Modal (略，保持原狀但可優化) -->
    <div v-if="editingSkill" class="modal-overlay" @click.self="cancelEdit">
      <div class="modal-card card shadow-lg">
        <div class="modal-header">
          <h3>編輯技能：{{ editingSkill.name }}</h3>
        </div>
        
        <div class="modal-body">
          <div class="form-group mb-4">
            <label class="form-label">描述</label>
            <textarea v-model="editForm.description" rows="3" class="form-input" placeholder="輸入技能描述..."></textarea>
          </div>
          <div class="form-group mb-4">
            <label class="form-label">作者</label>
            <input v-model="editForm.author" class="form-input" placeholder="作者名稱" />
          </div>
          <div class="form-group mb-4">
            <label class="form-label">標籤 (以逗號分隔)</label>
            <input v-model="editForm.tagsString" class="form-input" placeholder="例如: web, search, ai" />
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-ghost" @click="cancelEdit">取消</button>
          <button class="btn-primary" @click="saveEdit" :disabled="saving">
            {{ saving ? '儲存中...' : '儲存修改' }}
          </button>
        </div>
      </div>
    </div>


    <!-- 使用者編輯/新增 Modal -->
    <div v-if="editingUser || isCreatingUser" class="modal-overlay" @click.self="cancelEditUser">
      <div class="modal-card card shadow-lg">
        <div class="modal-header">
          <h3>{{ isCreatingUser ? '新增使用者' : '編輯使用者：' + editingUser.username }}</h3>
        </div>
        
        <div class="modal-body">
          <div class="form-group mb-4">
            <label class="form-label">使用者名稱</label>
            <input v-model="userForm.username" class="form-input" placeholder="例如: john_doe" />
          </div>
          <div class="form-group mb-4">
            <label class="form-label">Email 地址</label>
            <input v-model="userForm.email" class="form-input" placeholder="例如: john@example.com" />
          </div>
          <div class="form-group mb-4">
            <label class="form-label">系統角色</label>
            <select v-model="userForm.role" class="custom-select">
              <option value="admin">Admin (管理員 - 全域權限)</option>
              <option value="maintainer">Maintainer (開發者 - 可發布與更新)</option>
              <option value="user">User (一般用戶 - 僅限讀取)</option>
            </select>
          </div>
          <div class="form-group mb-4">
            <label class="form-label">具體權限點</label>
            <div class="permission-grid">
              <label v-for="p in ALL_PERMISSIONS" :key="p" class="checkbox-item">
                <input type="checkbox" :value="p" v-model="userForm.permissions" />
                <span>{{ p }}</span>
              </label>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-ghost" @click="cancelEditUser">取消</button>
          <button class="btn-primary" @click="saveUserEdit" :disabled="saving">
            {{ saving ? '處理中...' : (isCreatingUser ? '確認建立' : '確認修改') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const currentTab = ref('skills')
const skills = ref([])
const users = ref([])
const stats = ref({})
const searchQuery = ref('')
const userSearchQuery = ref('')

// 分頁狀態
const skillPagination = reactive({ page: 1, total: 0, pages: 1, per_page: 15 })
const userPagination = reactive({ page: 1, total: 0, pages: 1, per_page: 15 })

const editingSkill = ref(null)
const editForm = ref({ description: '', author: '', tagsString: '' })

const editingUser = ref(null)
const isCreatingUser = ref(false)
const userForm = reactive({ username: '', email: '', role: 'user', permissions: [] })
const ALL_PERMISSIONS = ['skill:create', 'skill:update', 'skill:delete', 'admin:access']

const saving = ref(false)

async function fetchData(page = 1) {
  skillPagination.page = page
  try {
    const headers = { 'Authorization': `Bearer ${authStore.token}` }
    const [skillsRes, statsRes] = await Promise.all([
      fetch(`/api/admin/skills?q=${searchQuery.value}&page=${page}&per_page=${skillPagination.per_page}`, { headers }),
      fetch('/api/skills/stats')
    ])
    if (skillsRes.status === 401) { authStore.logout(); return }
    
    const skillsData = await skillsRes.json()
    skills.value = skillsData.skills || []
    skillPagination.total = skillsData.total
    skillPagination.pages = skillsData.pages
    
    stats.value = await statsRes.json()
  } catch (e) {
    console.error('Failed to fetch admin skills', e)
  }
}

async function fetchUsers(page = 1) {
  userPagination.page = page
  try {
    const res = await fetch(`/api/admin/users?q=${userSearchQuery.value}&page=${page}&per_page=${userPagination.per_page}`, {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (res.ok) {
        const data = await res.json()
        users.value = data.users || []
        userPagination.total = data.total
        userPagination.pages = data.pages
    }
  } catch (e) {
    console.error('Failed to fetch users', e)
  }
}

watch(currentTab, (newTab) => {
  if (newTab === 'users') fetchUsers()
  else fetchData()
})

let timeout = null
function debouncedFetch() {
  clearTimeout(timeout)
  timeout = setTimeout(() => fetchData(1), 300)
}

let userTimeout = null
function debouncedFetchUsers() {
  clearTimeout(userTimeout)
  userTimeout = setTimeout(() => fetchUsers(1), 300)
}

// 技能操作
function editSkill(skill) {
  editingSkill.value = skill
  editForm.value = {
    description: skill.description,
    author: skill.author,
    tagsString: (skill.tags || []).join(', ')
  }
}

function cancelEdit() { editingSkill.value = null }

async function saveEdit() {
  saving.value = true
  try {
    const payload = {
      description: editForm.value.description,
      author: editForm.value.author,
      tags: editForm.value.tagsString.split(',').map(t => t.trim()).filter(Boolean)
    }
    const res = await fetch(`/api/admin/skills/${editingSkill.value.name}`, {
      method: 'PATCH',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify(payload)
    })
    if (res.ok) {
      await fetchData(skillPagination.page)
      cancelEdit()
    }
  } catch (e) {
    alert('儲存失敗')
  } finally {
    saving.value = false
  }
}

async function confirmDelete(skill) {
  if (!confirm(`確定要永久刪除技能 "${skill.name}" 嗎？`)) return
  try {
    const res = await fetch(`/api/admin/skills/${skill.name}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (res.ok) fetchData(skillPagination.page)
  } catch (e) {
    alert('刪除失敗')
  }
}

// 使用者操作
function createUser() {
  isCreatingUser.ref = true
  editingUser.value = null
  userForm.username = ''
  userForm.email = ''
  userForm.role = 'user'
  userForm.permissions = []
  isCreatingUser.value = true
}

function editUser(user) {
  isCreatingUser.value = false
  editingUser.value = user
  userForm.username = user.username
  userForm.email = user.email
  userForm.role = user.role
  userForm.permissions = [...(user.permissions || [])]
}

function cancelEditUser() { 
  editingUser.value = null
  isCreatingUser.value = false
}

async function saveUserEdit() {
  saving.value = true
  try {
    const isNew = isCreatingUser.value
    const url = isNew ? '/api/admin/users' : `/api/admin/users/${editingUser.value.id}`
    const method = isNew ? 'POST' : 'PATCH'
    
    const res = await fetch(url, {
      method: method,
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify(userForm)
    })
    
    if (res.ok) {
      await fetchUsers(userPagination.page)
      cancelEditUser()
    } else {
      const err = await res.json()
      alert(err.message || '操作失敗')
    }
  } catch (e) {
    alert('操作失敗')
  } finally {
    saving.value = false
  }
}

async function deleteUser(user) {
  if (!confirm(`確定要刪除使用者 "${user.username}" 嗎？`)) return
  try {
    const res = await fetch(`/api/admin/users/${user.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (res.ok) fetchUsers(userPagination.page)
  } catch (e) {
    alert('刪除失敗')
  }
}

onMounted(() => {
  if (currentTab.value === 'skills') fetchData(1)
  else fetchUsers(1)
})
</script>

<style scoped>
.admin-page { padding: 2rem; max-width: 1200px; margin: 0 auto; }
.admin-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem; }
.subtitle { color: var(--text-secondary); font-size: 0.95rem; margin-top: 0.3rem; }

.tabs-nav { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 1px; }
.tabs-nav button {
  padding: 0.8rem 1.5rem; border: none; background: transparent; color: var(--text-muted);
  font-weight: 600; cursor: pointer; transition: all 0.2s; border-bottom: 2px solid transparent;
  font-size: 0.9rem;
}
.tabs-nav button:hover { color: var(--text-primary); }
.tabs-nav button.active { color: var(--accent); border-bottom-color: var(--accent); }

.stats-cards { display: flex; gap: 1rem; }
.stat-card {
  background: var(--bg-card); border: 1px solid var(--border); padding: 1rem 1.2rem;
  border-radius: 12px; display: flex; flex-direction: column; min-width: 130px;
}
.stat-label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; }
.stat-value { font-size: 1.6rem; font-weight: 700; color: var(--accent); }

.admin-content { padding: 1.5rem; background: var(--bg-secondary); border-color: var(--border-subtle); overflow: hidden; }
.toolbar { display: flex; justify-content: space-between; margin-bottom: 1.2rem; gap: 1rem; }
.search-box { flex: 1; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 8px; padding: 0 1rem; display: flex; align-items: center; gap: 0.6rem; }
.search-box input { background: transparent; border: none; color: #fff; padding: 0.6rem 0; width: 100%; outline: none; font-size: 0.9rem; }

.admin-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.admin-table th { text-align: left; padding: 0.8rem 1rem; border-bottom: 2px solid var(--border); color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; }
.admin-table td { padding: 0.8rem 1rem; border-bottom: 1px solid var(--border-subtle); }

.role-badge { font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; }
.role-badge.admin { background: rgba(168, 85, 247, 0.2); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.3); }
.role-badge.maintainer { background: rgba(37, 164, 100, 0.2); color: var(--accent); border: 1px solid rgba(37, 164, 100, 0.3); }
.role-badge.user { background: rgba(107, 114, 128, 0.2); color: var(--text-muted); }

.permission-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; background: var(--bg-primary); padding: 1rem; border-radius: 8px; border: 1px solid var(--border); }
.checkbox-item { display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem; cursor: pointer; }
.checkbox-item input { accent-color: var(--accent); }

.custom-select { width: 100%; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 8px; padding: 0.6rem 1rem; color: #fff; outline: none; appearance: none; }

.modal-card { width: 100%; max-width: 500px; padding: 2rem; border-radius: 16px; background: var(--bg-secondary); border: 1px solid var(--border); }
.modal-header { margin-bottom: 1.5rem; border-bottom: 1px solid var(--border-subtle); padding-bottom: 1rem; }
.modal-header h3 { font-size: 1.25rem; font-weight: 700; color: #fff; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; z-index: 1000; backdrop-filter: blur(4px); padding: 1rem; }
.modal-footer { display: flex; justify-content: flex-end; gap: 0.8rem; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border-subtle); }

.form-group { display: flex; flex-direction: column; gap: 0.5rem; }
.form-label { font-size: 0.85rem; font-weight: 600; color: var(--text-secondary); }
.form-input {
  width: 100%; padding: 0.75rem 1rem; background: var(--bg-primary); 
  border: 1px solid var(--border); border-radius: 8px; color: #fff; 
  outline: none; transition: all 0.2s; font-size: 0.9rem;
}
.form-input:focus { border-color: var(--accent); box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2); }
textarea.form-input { resize: vertical; min-height: 100px; }

.mb-4 { margin-bottom: 1rem; }
.shadow-lg { box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3); }

.tag { font-size: 0.65rem; padding: 1px 6px; }
.btn-action { padding: 4px 12px; border-radius: 6px; border: none; cursor: pointer; font-size: 0.75rem; font-weight: 600; transition: all 0.2s; }
.btn-action.edit { background: rgba(34, 197, 94, 0.1); color: var(--accent); border: 1px solid rgba(34, 197, 94, 0.2); }
.btn-action.edit:hover { background: var(--accent); color: #fff; }
.btn-action.delete { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); margin-left: 0.5rem; }
.btn-action.delete:hover { background: #ef4444; color: #fff; }

.pagination { display: flex; align-items: center; justify-content: center; gap: 1rem; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border-subtle); }
.pagination button { padding: 0.5rem 1rem; background: var(--bg-primary); border: 1px solid var(--border); color: var(--text-secondary); border-radius: 6px; cursor: pointer; transition: all 0.2s; font-size: 0.85rem; font-weight: 600; }
.pagination button:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); }
.pagination button:disabled { opacity: 0.5; cursor: not-allowed; }
.page-info { font-size: 0.85rem; color: var(--text-muted); }

.toolbar-actions { display: flex; gap: 0.8rem; }
</style>

