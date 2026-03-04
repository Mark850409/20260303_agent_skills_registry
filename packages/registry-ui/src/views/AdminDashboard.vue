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
      <button :class="{ active: currentTab === 'mcps' }" @click="currentTab = 'mcps'">MCP 管理</button>
      <button :class="{ active: currentTab === 'users' }" @click="currentTab = 'users'">使用者管理</button>
    </div>

    <!-- 技能管理頁面 -->
    <div v-if="currentTab === 'skills'" class="admin-content card">
      <div class="toolbar">
        <div class="search-box">
          <span class="icon">🔍</span>
          <input v-model="searchQuery" placeholder="搜尋技能名稱或描述..." @input="debouncedFetch" />
        </div>
        <div class="toolbar-right">
          <!-- 每頁筆數 -->
          <div class="per-page-wrap">
            <span class="per-page-label">每頁</span>
            <select class="per-page-select" v-model="skillPerPage" @change="fetchData(1)">
              <option :value="5">5 筆</option>
              <option :value="10">10 筆</option>
              <option :value="20">20 筆</option>
              <option :value="50">50 筆</option>
            </select>
          </div>
          <!-- 視圖切換 -->
          <div class="view-toggle">
            <button
              class="view-btn"
              :class="{ active: skillViewMode === 'list' }"
              @click="skillViewMode = 'list'"
              title="列表視圖"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <rect x="1" y="2" width="14" height="2" rx="1"/>
                <rect x="1" y="7" width="14" height="2" rx="1"/>
                <rect x="1" y="12" width="14" height="2" rx="1"/>
              </svg>
            </button>
            <button
              class="view-btn"
              :class="{ active: skillViewMode === 'grid' }"
              @click="skillViewMode = 'grid'"
              title="卡片視圖"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <rect x="1" y="1" width="6" height="6" rx="1"/>
                <rect x="9" y="1" width="6" height="6" rx="1"/>
                <rect x="1" y="9" width="6" height="6" rx="1"/>
                <rect x="9" y="9" width="6" height="6" rx="1"/>
              </svg>
            </button>
          </div>
          <button class="btn-ai-classify" @click="classifyAll" :disabled="classifyingAll">
            {{ classifyingAll ? '⏳ 分類中...' : '🤖 AI 自動分類全部' }}
          </button>
          <button class="btn-ghost" @click="fetchData(1)">刷新數據</button>
        </div>
      </div>

      <!-- 批次操作 bar (Skills) -->
      <div v-if="selectedSkills.size > 0" class="batch-bar">
        <span class="batch-info">已選取 <strong>{{ selectedSkills.size }}</strong> 筆</span>
        <button class="btn-select-all" @click="toggleSelectAllSkills">
          {{ selectedSkills.size === skills.length ? '取消全選' : '全選' }}
        </button>
        <button class="btn-batch-delete" @click="batchDeleteSkills" :disabled="batchDeleting">
          {{ batchDeleting ? '刪除中…' : '🗑 删除選取項目' }}
        </button>
        <button class="btn-batch-cancel" @click="clearSelectedSkills">取消選取</button>
      </div>
      <div v-if="skillViewMode === 'list'" class="table-container">
        <table class="admin-table">
          <thead>
            <tr>
              <th class="cb-col">
                <input type="checkbox" class="batch-cb"
                  :checked="skills.length > 0 && selectedSkills.size === skills.length"
                  :indeterminate.prop="selectedSkills.size > 0 && selectedSkills.size < skills.length"
                  @change="toggleSelectAllSkills"
                />
              </th>
              <th>技能名稱</th>
              <th>作者</th>
              <th>分類</th>
              <th>標籤</th>
              <th>下載次數</th>
              <th>最新版本</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="skill in skills" :key="skill.id" :class="{ 'row-selected': selectedSkills.has(skill.name) }">
              <td class="cb-col">
                <input type="checkbox" class="batch-cb"
                  :checked="selectedSkills.has(skill.name)"
                  @change="toggleSkillSelect(skill.name)"
                />
              </td>
              <td class="skill-name-cell">
                <span class="skill-name">{{ skill.name }}</span>
              </td>
              <td>{{ skill.author }}</td>
              <!-- 分類欄位 -->
              <td class="category-cell">
                <select
                  class="category-select"
                  :value="skill.category || ''"
                  @change="setSkillCategory(skill, $event.target.value)"
                >
                  <option value="">— 未分類 —</option>
                  <option v-for="cat in CATEGORIES" :key="cat.id" :value="cat.id">
                    {{ cat.icon }} {{ cat.label }}
                  </option>
                </select>
              </td>
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
              <td colspan="8">尚無任何技能數據</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 卡片視圖 -->
      <div v-else class="skill-cards-grid">
        <div v-if="skills.length === 0" class="cards-empty">尚無任何技能數據</div>
        <div v-for="skill in skills" :key="skill.id" class="skill-card-admin">
          <div class="card-head">
            <div class="card-icon">🧩</div>
            <div class="card-meta">
              <div class="card-name">{{ skill.name }}</div>
              <div class="card-author">@{{ skill.author }}</div>
            </div>
            <code class="card-version">v{{ skill.latest_version }}</code>
          </div>
          <!-- 分類 badge -->
          <div class="card-category">
            <select
              class="category-select"
              :value="skill.category || ''"
              @change="setSkillCategory(skill, $event.target.value)"
            >
              <option value="">— 未分類 —</option>
              <option v-for="cat in CATEGORIES" :key="cat.id" :value="cat.id">
                {{ cat.icon }} {{ cat.label }}
              </option>
            </select>
          </div>
          <div class="card-tags">
            <span v-for="tag in (skill.tags || []).slice(0, 4)" :key="tag" class="tag">{{ tag }}</span>
            <span v-if="!(skill.tags || []).length" class="no-tag">無標籤</span>
          </div>
          <div class="card-stats">
            <span class="card-stat">⬇ {{ skill.downloads }} 次下載</span>
          </div>
          <div class="card-actions">
            <button class="btn-action edit" @click="editSkill(skill)">編輯</button>
            <button class="btn-action delete" @click="confirmDelete(skill)">刪除</button>
          </div>
        </div>
      </div>

      <!-- 技能分頁 -->
      <div class="pagination" v-if="skillPagination.pages >= 1">
        <button :disabled="skillPagination.page === 1" @click="fetchData(skillPagination.page - 1)">上一頁</button>
        <span class="page-info">
          第 {{ skillPagination.page }} / {{ skillPagination.pages }} 頁 (共 {{ skillPagination.total }} 筆，每頁 {{ skillPerPage }} 筆)
        </span>
        <button :disabled="skillPagination.page === skillPagination.pages" @click="fetchData(skillPagination.page + 1)">下一頁</button>
      </div>
    </div>

    <div v-if="currentTab === 'mcps'" class="admin-content card">
      <div class="toolbar">
        <div class="search-box">
          <span class="icon">🔍</span>
          <input v-model="mcpSearchQuery" placeholder="搜尋 MCP 名稱..." @input="debouncedFetchMcps" />
        </div>
        <div class="toolbar-right">
          <!-- MCP 每頁筆數 -->
          <div class="per-page-wrap">
            <span class="per-page-label">每頁</span>
            <select class="per-page-select" v-model="mcpPerPage" @change="fetchMcps(1)">
              <option :value="5">5 筆</option>
              <option :value="10">10 筆</option>
              <option :value="20">20 筆</option>
              <option :value="50">50 筆</option>
            </select>
          </div>
          <!-- MCP 視圖切換 -->
          <div class="view-toggle">
            <button
              class="view-btn"
              :class="{ active: mcpViewMode === 'list' }"
              @click="mcpViewMode = 'list'"
              title="列表視圖"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <rect x="1" y="2" width="14" height="2" rx="1"/>
                <rect x="1" y="7" width="14" height="2" rx="1"/>
                <rect x="1" y="12" width="14" height="2" rx="1"/>
              </svg>
            </button>
            <button
              class="view-btn"
              :class="{ active: mcpViewMode === 'grid' }"
              @click="mcpViewMode = 'grid'"
              title="卡片視圖"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <rect x="1" y="1" width="6" height="6" rx="1"/>
                <rect x="9" y="1" width="6" height="6" rx="1"/>
                <rect x="1" y="9" width="6" height="6" rx="1"/>
                <rect x="9" y="9" width="6" height="6" rx="1"/>
              </svg>
            </button>
          </div>
          <button class="btn-ai-classify" @click="classifyAllMcps" :disabled="classifyingMcps">
            {{ classifyingMcps ? '⏳ 分類中...' : '🤖 AI 自動分類全部 MCP' }}
          </button>
          <button class="btn-ghost" @click="fetchMcps(1)">刷新數據</button>
        </div>
      </div>

      <!-- 批次操作 bar (MCP) -->
      <div v-if="selectedMcps.size > 0" class="batch-bar mcp-batch-bar">
        <span class="batch-info">已選取 <strong>{{ selectedMcps.size }}</strong> 筆</span>
        <button class="btn-select-all" @click="toggleSelectAllMcps">
          {{ selectedMcps.size === mcps.length ? '取消全選' : '全選' }}
        </button>
        <button class="btn-batch-delete" @click="batchDeleteMcps" :disabled="batchDeletingMcp">
          {{ batchDeletingMcp ? '刪除中…' : '🗑 删除選取項目' }}
        </button>
        <button class="btn-batch-cancel" @click="clearSelectedMcps">取消選取</button>
      </div>

      <!-- MCP 列表視圖 -->
      <div v-if="mcpViewMode === 'list'" class="table-container">
        <table class="admin-table text-xs">
          <thead>
            <tr>
              <th class="cb-col">
                <input type="checkbox" class="batch-cb"
                  :checked="mcps.length > 0 && selectedMcps.size === mcps.length"
                  :indeterminate="selectedMcps.size > 0 && selectedMcps.size < mcps.length"
                  @change="toggleSelectAllMcps"
                />
              </th>
              <th>MCP 名稱</th>
              <th>傳輸</th>
              <th>分類</th>
              <th>作者</th>
              <th>連線數</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="mcp in mcps" :key="mcp.id" :class="{ 'row-selected': selectedMcps.has(mcp.name) }">
              <td class="cb-col">
                <input type="checkbox" class="batch-cb"
                  :checked="selectedMcps.has(mcp.name)"
                  @change="toggleMcpSelect(mcp.name)"
                />
              </td>
              <td>
                <div class="font-bold text-white">{{ mcp.display_name }}</div>
                <div class="text-[10px] text-muted">{{ mcp.name }}</div>
              </td>
              <td>
                <span :class="['transport-badge', mcp.transport]">{{ mcp.transport }}</span>
              </td>
              <td class="category-cell">
                <select
                  class="category-select"
                  :value="mcp.category || ''"
                  @change="setMcpCategory(mcp, $event.target.value)"
                >
                  <option value="">— 未分類 —</option>
                  <option v-for="cat in MCP_CATEGORIES" :key="cat.id" :value="cat.id">
                    {{ cat.icon }} {{ cat.label }}
                  </option>
                </select>
              </td>
              <td>{{ mcp.author }}</td>
              <td>{{ mcp.installs || 0 }}</td>
              <td class="actions">
                <button class="btn-action edit" @click="editMcp(mcp)">編輯</button>
                <button class="btn-action delete" @click="confirmDeleteMcp(mcp)">刪除</button>
              </td>
            </tr>
            <tr v-if="mcps.length === 0" class="empty-row">
              <td colspan="7">尚無任何 MCP 數據</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- MCP 卡片視圖 -->
      <div v-else class="skill-cards-grid">
        <div v-if="mcps.length === 0" class="cards-empty">尚無任何 MCP 數據</div>
        <div v-for="mcp in mcps" :key="mcp.id" class="skill-card-admin">
          <div class="card-head">
            <div class="card-icon">🔌</div>
            <div class="card-meta">
              <div class="card-name">{{ mcp.display_name }}</div>
              <div class="card-author">@{{ mcp.author }}</div>
            </div>
            <span :class="['transport-badge', mcp.transport]">{{ mcp.transport }}</span>
          </div>
          <div class="card-category">
            <select
              class="category-select"
              :value="mcp.category || ''"
              @change="setMcpCategory(mcp, $event.target.value)"
            >
              <option value="">— 未分類 —</option>
              <option v-for="cat in MCP_CATEGORIES" :key="cat.id" :value="cat.id">
                {{ cat.icon }} {{ cat.label }}
              </option>
            </select>
          </div>
          <p class="card-stats">
            ID: <code>{{ mcp.name }}</code>
          </p>
          <div class="card-stats">
            <span class="card-stat">🔗 {{ mcp.installs || 0 }} 次連線</span>
          </div>
          <div class="card-actions">
            <button class="btn-action edit" @click="editMcp(mcp)">編輯</button>
            <button class="btn-action delete" @click="confirmDeleteMcp(mcp)">刪除</button>
          </div>
        </div>
      </div>

      <!-- MCP 分頁 -->
      <div class="pagination" v-if="mcpPagination.pages >= 1">
        <button :disabled="mcpPagination.page === 1" @click="fetchMcps(mcpPagination.page - 1)">上一頁</button>
        <span class="page-info">
          第 {{ mcpPagination.page }} / {{ mcpPagination.pages }} 頁 (共 {{ mcpPagination.total }} 筆，每頁 {{ mcpPerPage }} 筆)
        </span>
        <button :disabled="mcpPagination.page === mcpPagination.pages" @click="fetchMcps(mcpPagination.page + 1)">下一頁</button>
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

// 視圖模式
const skillViewMode = ref('list')  // 'list' | 'grid'

// 每頁筆數
const skillPerPage = ref(10)
const userPerPage = ref(15)

// 分頁狀態
const skillPagination = reactive({ page: 1, total: 0, pages: 1 })
const userPagination = reactive({ page: 1, total: 0, pages: 1 })

// ── 分類常數（與後端 CATEGORIES 同步） ──
const CATEGORIES = [
  { id: 'coding',        label: '程式開發',    icon: '💻' },
  { id: 'web',           label: 'Web / UI',   icon: '🌐' },
  { id: 'data',          label: '資料分析',    icon: '📊' },
  { id: 'writing',       label: '文案 / 文件', icon: '✍️'  },
  { id: 'ai',            label: 'AI / Agent', icon: '🤖' },
  { id: 'design',        label: '設計 / 創作', icon: '🎨' },
  { id: 'productivity',  label: '效率工具',    icon: '⚡' },
  { id: 'devops',        label: 'DevOps',     icon: '🛠️' },
]

const MCP_CATEGORIES = [
  { id: 'coding',        icon: '💻', label: 'Dev Tools & Coding' },
  { id: 'web',           icon: '🌐', label: 'Web 瀏覽' },
  { id: 'search',        icon: '🔍', label: '網路搜尋' },
  { id: 'data',          icon: '📊', label: 'Data & Analytics' },
  { id: 'database',      icon: '🗄️', label: 'Database & SQL' },
  { id: 'ai',            icon: '🤖', label: 'AI 智能' },
  { id: 'productivity',  icon: '⚡', label: 'Productivity' },
  { id: 'writing',       icon: '✍️', label: '文案文件' },
  { id: 'design',        icon: '🎨', label: '設計創作' },
  { id: 'devops',        icon: '🛠️', label: '運維部署' },
  { id: 'communication', icon: '💬', label: '通訊聯絡' },
  { id: 'maps',          icon: '📍', label: 'Maps & Geodata' },
  { id: 'finance',       icon: '💰', label: 'Finance & Crypto' },
  { id: 'science',       icon: '🧪', label: 'Science & Math' },
  { id: 'travel',        icon: '✈️',  label: 'Travel & Lifestyle' },
  { id: 'health',        icon: '🏥', label: 'Health & Fitness' },
  { id: 'other',         icon: '📦', label: '其他' },
]

const mcpViewMode = ref('list')
const mcpPerPage = ref(10)

const mcps = ref([])
const mcpSearchQuery = ref('')
const mcpPagination = reactive({ page: 1, total: 0, pages: 1 })
const classifyingMcps = ref(false)
const editingMcp = ref(null)

const classifyingAll = ref(false)

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
      fetch(`/api/admin/skills?q=${searchQuery.value}&page=${page}&per_page=${skillPerPage.value}`, { headers }),
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
    const res = await fetch(`/api/admin/users?q=${userSearchQuery.value}&page=${page}&per_page=${userPerPage.value}`, {
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

// ── 分類管理 ──────────────────────────────────────────────────────

/** AI 批次自動分類全部技能 */
async function classifyAll() {
  if (!confirm('將由 AI 自動分類所有技能（會覆蓋現有分類），確定執行？')) return
  classifyingAll.value = true
  try {
    const res = await fetch('/api/admin/skills/classify-all', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (!res.ok) { alert('分類失敗，請確認登入狀態'); return }
    const data = await res.json()
    alert(`✅ 完成！已自動分類 ${data.classified} 個技能（${data.skipped} 個無法判斷）`)
    await fetchData(skillPagination.page)
  } catch (e) {
    console.error('classifyAll error', e)
  } finally {
    classifyingAll.value = false
  }
}

/** 手動設定單一技能分類 */
async function setSkillCategory(skill, categoryId) {
  const oldCategory = skill.category
  skill.category = categoryId || null  // 樂觀更新
  try {
    const res = await fetch(`/api/admin/skills/${skill.name}`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ category: categoryId || null })
    })
    if (!res.ok) {
      skill.category = oldCategory  // 回滾
      alert('更新分類失敗')
    }
  } catch (e) {
    skill.category = oldCategory
    console.error('setSkillCategory error', e)
  }
}


async function fetchMcps(page = 1) {
  mcpPagination.page = page
  try {
    const res = await fetch(`/api/admin/mcps?q=${mcpSearchQuery.value}&page=${page}&per_page=${mcpPerPage.value}`, {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    const data = await res.json()
    mcps.value = data.mcps || []
    mcpPagination.total = data.total
    mcpPagination.pages = data.pages
  } catch (e) {
    console.error('fetchMcps error', e)
  }
}

async function classifyAllMcps() {
  if (!confirm('將由 AI 自動分類所有 MCP Server，確定執行？')) return
  classifyingMcps.value = true
  try {
    const res = await fetch('/api/admin/mcps/classify-all', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    const data = await res.json()
    alert(`✅ 完成！已自動分類 ${data.classified} 個 MCP Server`)
    await fetchMcps(1)
  } finally {
    classifyingMcps.value = false
  }
}

async function setMcpCategory(mcp, catId) {
  const old = mcp.category
  mcp.category = catId || null
  try {
    const res = await fetch(`/api/admin/mcps/${mcp.name}`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ category: catId || null })
    })
    if (!res.ok) throw new Error()
  } catch {
    mcp.category = old
    alert('更新失敗')
  }
}

let mcpTimeout = null
function debouncedFetchMcps() {
  clearTimeout(mcpTimeout)
  mcpTimeout = setTimeout(() => fetchMcps(1), 300)
}

watch(currentTab, (newTab) => {
  if (newTab === 'users') fetchUsers()
  else if (newTab === 'mcps') fetchMcps()
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

// MCP 操作
function editMcp(mcp) {
  editingMcp.value = mcp
  // 這裡複用編輯 Modal。注意：MCP 與 Skill 欄位名稱不同（display_name vs name），Modal 需要稍後做條件渲染
  editingSkill.value = null 
  editSkill(mcp) 
}

async function confirmDeleteMcp(mcp) {
  if (!confirm(`確定要永久刪除 MCP Server "${mcp.display_name}" 嗎？`)) return
  try {
    const res = await fetch(`/api/admin/mcps/${mcp.name}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (res.ok) fetchMcps(mcpPagination.page)
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

// ── 批次刪除 ──────────────────────────────────────────────────────
const selectedSkills = ref(new Set())
const selectedMcps = ref(new Set())
const batchDeleting = ref(false)
const batchDeletingMcp = ref(false)

function clearSelectedSkills() { selectedSkills.value = new Set() }
function clearSelectedMcps() { selectedMcps.value = new Set() }

function toggleSkillSelect(name) {
  const s = new Set(selectedSkills.value)
  s.has(name) ? s.delete(name) : s.add(name)
  selectedSkills.value = s
}

function toggleSelectAllSkills() {
  if (selectedSkills.value.size === skills.value.length) {
    selectedSkills.value = new Set()
  } else {
    selectedSkills.value = new Set(skills.value.map(s => s.name))
  }
}

async function batchDeleteSkills() {
  const names = [...selectedSkills.value]
  if (!names.length) return
  if (!confirm(`確定要永久刪除選取的 ${names.length} 筆技能嗎？此操作不可復原！`)) return
  batchDeleting.value = true
  try {
    await Promise.all(names.map(name =>
      fetch(`/api/admin/skills/${name}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${authStore.token}` }
      })
    ))
    selectedSkills.value = new Set()
    await fetchData(skillPagination.page)
  } catch (e) {
    alert('部分刪除失敗，請重新整理')
  } finally {
    batchDeleting.value = false
  }
}

function toggleMcpSelect(name) {
  const s = new Set(selectedMcps.value)
  s.has(name) ? s.delete(name) : s.add(name)
  selectedMcps.value = s
}

function toggleSelectAllMcps() {
  if (selectedMcps.value.size === mcps.value.length) {
    selectedMcps.value = new Set()
  } else {
    selectedMcps.value = new Set(mcps.value.map(m => m.name))
  }
}

async function batchDeleteMcps() {
  const names = [...selectedMcps.value]
  if (!names.length) return
  if (!confirm(`確定要永久刪除選取的 ${names.length} 筆 MCP Server 嗎？此操作不可復原！`)) return
  batchDeletingMcp.value = true
  try {
    await Promise.all(names.map(name =>
      fetch(`/api/admin/mcps/${name}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${authStore.token}` }
      })
    ))
    selectedMcps.value = new Set()
    await fetchMcps(mcpPagination.page)
  } catch (e) {
    alert('部分刪除失敗，請重新整理')
  } finally {
    batchDeletingMcp.value = false
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
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem; gap: 1rem; flex-wrap: wrap; }
.toolbar-right { display: flex; align-items: center; gap: 0.6rem; flex-shrink: 0; }
.search-box { flex: 1; min-width: 180px; background: var(--bg-primary); border: 1px solid var(--border); border-radius: 8px; padding: 0 1rem; display: flex; align-items: center; gap: 0.6rem; }
.search-box input { background: transparent; border: none; color: #fff; padding: 0.6rem 0; width: 100%; outline: none; font-size: 0.9rem; }

/* 每頁筆數 */
.per-page-wrap { display: flex; align-items: center; gap: 0.4rem; }
.per-page-label { font-size: 0.78rem; color: var(--text-muted); white-space: nowrap; }
.per-page-select {
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  background: var(--bg-primary);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.8rem;
  outline: none;
  cursor: pointer;
  appearance: none;
}
.per-page-select:focus { border-color: var(--accent); }

/* AI 自動分類按鈕 */
.btn-ai-classify {
  padding: 0.3rem 0.8rem;
  border-radius: 7px;
  border: 1px solid var(--accent);
  background: var(--accent-dim);
  color: var(--accent);
  font-size: 0.8rem;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.15s;
  white-space: nowrap;
}
.btn-ai-classify:hover:not(:disabled) { background: var(--accent); color: #000; }
.btn-ai-classify:disabled { opacity: 0.5; cursor: not-allowed; }

/* 分類下拉 */
.category-cell { min-width: 140px; }
.category-select {
  width: 100%;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  background: var(--bg-primary);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.78rem;
  outline: none;
  cursor: pointer;
  appearance: none;
  min-width: 130px;
}
.category-select:focus { border-color: var(--accent); }
.card-category { margin-bottom: 0.2rem; }
.card-category .category-select { min-width: unset; }


/* 視圖切換 */
.view-toggle { display: flex; gap: 2px; border: 1px solid var(--border); border-radius: 7px; overflow: hidden; }
.view-btn {
  padding: 0.3rem 0.5rem;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}
.view-btn:hover { background: var(--bg-secondary); color: var(--text-primary); }
.view-btn.active { background: var(--accent-dim); color: var(--accent); }

/* 卡片視圖 */
.skill-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}
.cards-empty {
  grid-column: 1 / -1;
  text-align: center;
  padding: 3rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}
.skill-card-admin {
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.skill-card-admin:hover {
  border-color: rgba(37,164,100,0.4);
  box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}
.card-head { display: flex; align-items: flex-start; gap: 0.6rem; }
.card-icon { font-size: 1.4rem; line-height: 1; flex-shrink: 0; margin-top: 2px; }
.card-meta { flex: 1; min-width: 0; }
.card-name {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.card-author { font-size: 0.75rem; color: var(--text-muted); margin-top: 1px; }
.card-version {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: var(--accent);
  background: var(--accent-dim);
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
  align-self: flex-start;
}
.card-tags { display: flex; flex-wrap: wrap; gap: 0.3rem; min-height: 22px; }
.card-tags .tag { font-size: 0.65rem; }
.no-tag { font-size: 0.72rem; color: var(--text-muted); }
.card-stats { font-size: 0.75rem; color: var(--text-muted); }
.card-actions { display: flex; gap: 0.4rem; margin-top: 0.2rem; }

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

.transport-badge { font-size: 0.65rem; font-weight: 700; padding: 1px 6px; border-radius: 4px; text-transform: uppercase; }
.transport-badge.sse { background: rgba(59, 130, 246, 0.2); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.3); }
.transport-badge.stdio { background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }

.text-muted { color: var(--text-muted); }
.text-xs { font-size: 0.75rem; }

/* ── 批次刪除 ── */
.cb-col { width: 36px; text-align: center; padding: 0 6px !important; }
.batch-cb {
  width: 16px; height: 16px; cursor: pointer;
  accent-color: var(--accent);
}
.row-selected { background: rgba(34, 197, 94, 0.05) !important; }
.row-selected td { color: var(--text-primary); }

.batch-bar {
  display: flex; align-items: center; gap: 0.75rem;
  background: var(--bg-card);
  border: 1px solid rgba(34, 197, 94, 0.35);
  border-radius: 10px;
  padding: 0.65rem 1rem;
  margin-bottom: 0.75rem;
  animation: batchBarIn 0.2s ease;
}
.mcp-batch-bar { border-color: rgba(249, 115, 22, 0.35); }
@keyframes batchBarIn {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.batch-info { font-size: 0.85rem; color: var(--text-secondary); flex: 1; }
.batch-info strong { color: var(--accent); }
.mcp-batch-bar .batch-info strong { color: #f97316; }

.btn-select-all {
  padding: 4px 12px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; cursor: pointer;
  background: rgba(34, 197, 94, 0.1); color: var(--accent);
  border: 1px solid rgba(34, 197, 94, 0.25);
  transition: background 0.15s;
}
.btn-select-all:hover { background: rgba(34, 197, 94, 0.2); }

.btn-batch-delete {
  padding: 4px 14px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; cursor: pointer;
  background: rgba(239, 68, 68, 0.15); color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
  transition: background 0.15s;
}
.btn-batch-delete:hover:not(:disabled) { background: #ef4444; color: #fff; }
.btn-batch-delete:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-batch-cancel {
  padding: 4px 12px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; cursor: pointer;
  background: transparent; color: var(--text-muted);
  border: 1px solid var(--border);
  transition: all 0.15s;
}
.btn-batch-cancel:hover { color: var(--text-primary); border-color: var(--text-muted); }
</style>

