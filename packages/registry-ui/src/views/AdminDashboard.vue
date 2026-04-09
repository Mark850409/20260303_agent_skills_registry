<template>
  <div class="admin-layout fade-up">
    <aside class="admin-sidebar" :class="{ collapsed: isSidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo" v-if="!isSidebarCollapsed">
          <span class="logo-icon">🧠</span>
          <span class="logo-text">管理控制中心</span>
        </div>
        <button class="hamburger-btn" @click="isSidebarCollapsed = !isSidebarCollapsed">
          <span class="icon">{{ isSidebarCollapsed ? '☰' : '✕' }}</span>
        </button>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-group">
          <div class="group-title" v-if="!isSidebarCollapsed">核心管理</div>
          <button :class="{ active: currentTab === 'skills' }" @click="currentTab = 'skills'" title="技能管理">
            <span class="icon">🧩</span>
            <span class="label" v-if="!isSidebarCollapsed">技能管理</span>
          </button>
          <button :class="{ active: currentTab === 'mcps' }" @click="currentTab = 'mcps'" title="MCP 管理">
            <span class="icon">🔌</span>
            <span class="label" v-if="!isSidebarCollapsed">MCP 管理</span>
          </button>
        </div>

        <div class="nav-group">
          <div class="group-title" v-if="!isSidebarCollapsed">外部儲存庫</div>
          <button :class="{ active: currentTab === 'docker' }" @click="currentTab = 'docker'" title="容器管理">
            <span class="icon">⚓</span>
            <span class="label" v-if="!isSidebarCollapsed">容器管理</span>
          </button>
          <button :class="{ active: currentTab === 'npm' }" @click="currentTab = 'npm'" title="NPM 管理">
            <span class="icon">📦</span>
            <span class="label" v-if="!isSidebarCollapsed">NPM 管理</span>
          </button>
        </div>

        <div class="nav-group">
          <div class="group-title" v-if="!isSidebarCollapsed">提示詞工程</div>
          <button :class="{ active: currentTab === 'prompts' }" @click="currentTab = 'prompts'" title="提示詞設定">
            <span class="icon">✨</span>
            <span class="label" v-if="!isSidebarCollapsed">提示詞設定</span>
          </button>
          <button :class="{ active: currentTab === 'prompt-kb' }" @click="currentTab = 'prompt-kb'" title="提示詞知識庫">
            <span class="icon">💡</span>
            <span class="label" v-if="!isSidebarCollapsed">提示詞知識庫</span>
          </button>
        </div>

        <div class="nav-group">
          <div class="group-title" v-if="!isSidebarCollapsed">系統管理</div>
          <button :class="{ active: currentTab === 'users' }" @click="currentTab = 'users'" title="使用者管理">
            <span class="icon">👤</span>
            <span class="label" v-if="!isSidebarCollapsed">使用者管理</span>
          </button>
        </div>
      </nav>
    </aside>

    <main class="admin-main">
      <div class="admin-page-inner">
        <header class="admin-header">
          <div class="header-content">
            <h1>管理後台</h1>
            <p class="subtitle">
              <template v-if="currentTab === 'skills'">Registry 數據營運與管控中心</template>
              <template v-else-if="currentTab === 'mcps'">MCP 服務註冊與分析中心</template>
              <template v-else-if="currentTab === 'users'">系統帳號與權限核發中心</template>
              <template v-else-if="currentTab === 'docker'">Docker 容器映像管理與儲存庫</template>
              <template v-else-if="currentTab === 'npm'">NPM 套件管理與儲存庫</template>
            </p>
          </div>
          <div class="stats-cards">
            <template v-if="currentTab === 'skills'">
              <div class="stat-card">
                <span class="stat-label">總技能數</span>
                <span class="stat-value">{{ stats.total_skills || 0 }}</span>
              </div>
              <div class="stat-card">
                <span class="stat-label">累積下載</span>
                <span class="stat-value">{{ stats.total_downloads || 0 }}</span>
              </div>
            </template>
            <template v-else-if="currentTab === 'mcps'">
              <div class="stat-card">
                <span class="stat-label">總 MCP 數</span>
                <span class="stat-value">{{ mcpPagination.total || 0 }}</span>
              </div>
            </template>
            <template v-else-if="currentTab === 'users'">
              <div class="stat-card">
                <span class="stat-label">使用者總數</span>
                <span class="stat-value">{{ userPagination.total || 0 }}</span>
              </div>
            </template>
            <template v-else-if="currentTab === 'docker'">
              <div class="stat-card">
                <span class="stat-label">總倉庫數</span>
                <span class="stat-value">{{ dockerPagination.total || 0 }}</span>
              </div>
            </template>
            <template v-else-if="currentTab === 'npm'">
              <div class="stat-card">
                <span class="stat-label">總套件數</span>
                <span class="stat-value">{{ npmPagination.total || 0 }}</span>
              </div>
            </template>
            <template v-else-if="currentTab === 'prompts'">
              <div class="stat-card">
                <span class="stat-label">設定總數</span>
                <span class="stat-value">{{ prompts.length }}</span>
              </div>
            </template>
            <template v-else-if="currentTab === 'prompt-kb'">
              <div class="stat-card">
                <span class="stat-label">知識庫總數</span>
                <span class="stat-value">{{ promptKbEntries.length }}</span>
              </div>
            </template>
          </div>
        </header>

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
              <th @click="sortSkills('name')" class="sortable">
                技能名稱
                <span class="sort-icon">{{ skillSortField === 'name' ? (skillSortOrder === 'asc' ? '↑' : '↓') : '⇅' }}</span>
              </th>
              <th @click="sortSkills('author')" class="sortable">
                作者
                <span class="sort-icon">{{ skillSortField === 'author' ? (skillSortOrder === 'asc' ? '↑' : '↓') : '⇅' }}</span>
              </th>
              <th @click="sortSkills('category')" class="sortable">
                分類
                <span class="sort-icon">{{ skillSortField === 'category' ? (skillSortOrder === 'asc' ? '↑' : '↓') : '⇅' }}</span>
              </th>
              <th>標籤</th>
              <th @click="sortSkills('downloads')" class="sortable">
                下載次數
                <span class="sort-icon">{{ skillSortField === 'downloads' ? (skillSortOrder === 'asc' ? '↑' : '↓') : '⇅' }}</span>
              </th>
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
              <td class="actions-col">
                <div class="actions-container">
                  <button class="btn-action edit" @click="editSkill(skill)">編輯</button>
                  <button class="btn-action delete" @click="confirmDelete(skill)">刪除</button>
                </div>
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

    <!-- 容器管理頁面 -->
    <div v-else-if="currentTab === 'docker'" class="admin-content card">
      <div class="toolbar">
        <div class="search-box">
          <span class="icon">🔍</span>
          <input v-model="dockerSearchQuery" placeholder="搜尋倉庫名稱或描述..." @input="debouncedFetchDockerRepos" />
        </div>
        <div class="toolbar-actions">
          <button class="btn-primary" @click="createDockerRepo">+ 新增倉庫</button>
          <button class="btn-ghost" @click="fetchDockerRepos(1)">刷新清單</button>
        </div>
      </div>

      <div class="table-container">
        <table class="admin-table">
          <thead>
            <tr>
              <th>倉庫名稱</th>
              <th>描述</th>
              <th>建立時間</th>
              <th>更新時間</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="repo in dockerRepos" :key="repo.id">
              <td><strong>{{ repo.name }}</strong></td>
              <td>{{ repo.description || '無描述' }}</td>
              <td>{{ new Date(repo.created_at).toLocaleDateString() }}</td>
              <td>{{ new Date(repo.updated_at).toLocaleDateString() }}</td>
              <td class="actions">
                <button class="btn-action edit" @click="editDockerRepo(repo)">編輯</button>
                <button class="btn-action delete" @click="deleteDockerRepo(repo)">刪除</button>
              </td>
            </tr>
            <tr v-if="dockerRepos.length === 0" class="empty-row">
              <td colspan="5">尚無任何 Docker 倉庫資料</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Docker 倉庫分頁 -->
      <div class="pagination" v-if="dockerPagination.pages > 1">
        <button :disabled="dockerPagination.page === 1" @click="fetchDockerRepos(dockerPagination.page - 1)">上一頁</button>
        <span class="page-info">第 {{ dockerPagination.page }} / {{ dockerPagination.pages }} 頁 (共 {{ dockerPagination.total }} 筆)</span>
        <button :disabled="dockerPagination.page === dockerPagination.pages" @click="fetchDockerRepos(dockerPagination.page + 1)">下一頁</button>
      </div>
    </div>

    <!-- NPM 套件管理頁面 -->
    <div v-else-if="currentTab === 'npm'" class="admin-content card">
      <div class="toolbar">
        <div class="search-box">
          <span class="icon">🔍</span>
          <input v-model="npmSearchQuery" placeholder="搜尋套件名稱或描述..." @input="debouncedFetchNpmPackages" />
        </div>
        <div class="toolbar-actions">
          <button class="btn-primary" @click="createNpmPackage">+ 新增套件</button>
          <button class="btn-ghost" @click="fetchNpmPackages(1)">刷新清單</button>
        </div>
      </div>

      <div class="table-container">
        <table class="admin-table">
          <thead>
            <tr>
              <th>套件名稱</th>
              <th>描述</th>
              <th>建立時間</th>
              <th>更新時間</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pkg in npmPackages" :key="pkg.id">
              <td><strong>{{ pkg.name }}</strong></td>
              <td>{{ pkg.description || '無描述' }}</td>
              <td>{{ new Date(pkg.created_at).toLocaleDateString() }}</td>
              <td>{{ new Date(pkg.updated_at).toLocaleDateString() }}</td>
              <td class="actions">
                <button class="btn-action edit" @click="editNpmPackage(pkg)">編輯</button>
                <button class="btn-action delete" @click="deleteNpmPackage(pkg)">刪除</button>
              </td>
            </tr>
            <tr v-if="npmPackages.length === 0" class="empty-row">
              <td colspan="5">尚無任何 NPM 套件資料</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- NPM 套件分頁 -->
      <div class="pagination" v-if="npmPagination.pages > 1">
        <button :disabled="npmPagination.page === 1" @click="fetchNpmPackages(npmPagination.page - 1)">上一頁</button>
        <span class="page-info">第 {{ npmPagination.page }} / {{ npmPagination.pages }} 頁 (共 {{ npmPagination.total }} 筆)</span>
        <button :disabled="npmPagination.page === npmPagination.pages" @click="fetchNpmPackages(npmPagination.page + 1)">下一頁</button>
      </div>
    </div>

    <!-- 提示詞管理頁面 -->
    <div v-else-if="currentTab === 'prompts'" class="admin-content card">
      <div class="toolbar">
        <div class="toolbar-left" style="display: flex; gap: 1rem; flex: 1;">
          <div class="search-box" style="max-width: 300px;">
            <span class="icon">🔍</span>
            <input v-model="promptSearchQuery" placeholder="搜尋名稱或內容..." @input="debouncedFetchPrompts" />
          </div>
          <select v-model="promptCategoryFilter" @change="applyPromptFilters(1)" class="category-select" style="min-width: 160px;">
            <option value="">全部</option>
            <option v-for="cat in promptCategories" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
          </select>
        </div>
        <div class="toolbar-actions">
          <div class="per-page-wrap">
            <span class="per-page-label">每頁</span>
            <select class="per-page-select" v-model="promptPerPage" @change="applyPromptFilters(1)">
              <option :value="5">5 筆</option>
              <option :value="10">10 筆</option>
              <option :value="20">20 筆</option>
            </select>
          </div>
          <button class="btn-primary" @click="createPrompt">+ 新增設定</button>
          <button class="btn-ghost" @click="fetchPrompts(1)">刷新清單</button>
        </div>
      </div>

      <div class="table-container">
        <table class="admin-table">
          <thead>
            <tr>
              <th @click="sortPrompts('category')" class="sortable">
                分類 (Category)
                <span class="sort-icon">{{ promptSortField === 'category' ? (promptSortOrder === 'asc' ? '↑' : '↓') : '⇅' }}</span>
              </th>
              <th @click="sortPrompts('name')" class="sortable">
                名稱 / 內容 (Name)
                <span class="sort-icon">{{ promptSortField === 'name' ? (promptSortOrder === 'asc' ? '↑' : '↓') : '⇅' }}</span>
              </th>
              <th @click="sortPrompts('group_name')" class="sortable">
                群組 (Group)
                <span class="sort-icon">{{ promptSortField === 'group_name' ? (promptSortOrder === 'asc' ? '↑' : '↓') : '⇅' }}</span>
              </th>
              <th @click="sortPrompts('is_active')" class="sortable">
                狀態
                <span class="sort-icon">{{ promptSortField === 'is_active' ? (promptSortOrder === 'asc' ? '↑' : '↓') : '⇅' }}</span>
              </th>
              <th @click="sortPrompts('order_index')" class="sortable">
                排序權重
                <span class="sort-icon">{{ promptSortField === 'order_index' ? (promptSortOrder === 'asc' ? '↑' : '↓') : '⇅' }}</span>
              </th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="prompt in prompts" :key="prompt.id">
              <td>
                <span class="category-badge">{{ promptCategories.find(c => c.value === prompt.category)?.label || prompt.category }}</span>
              </td>
              <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                <strong>{{ prompt.name }}</strong>
              </td>
              <td>{{ prompt.group_name || '-' }}</td>
              <td>
                <span :class="prompt.is_active ? 'badge-active' : 'badge-inactive'">
                  {{ prompt.is_active ? '啟用' : '停用' }}
                </span>
              </td>
              <td><code>{{ prompt.order_index }}</code></td>
              <td class="actions-col">
                <div class="actions-container">
                  <button class="btn-action edit" @click="editPrompt(prompt)">編輯</button>
                  <button class="btn-action delete" @click="deletePrompt(prompt)">刪除</button>
                </div>
              </td>
            </tr>
            <tr v-if="prompts.length === 0" class="empty-row">
              <td colspan="6">尚無任何提示詞設定資料</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 提示詞分頁 -->
      <div class="pagination" v-if="promptPagination.pages >= 1">
        <button :disabled="promptPagination.page === 1" @click="applyPromptFilters(promptPagination.page - 1)">上一頁</button>
        <span class="page-info">
          第 {{ promptPagination.page }} / {{ promptPagination.pages }} 頁 (共 {{ promptPagination.total }} 筆，每頁 {{ promptPerPage }} 筆)
        </span>
        <button :disabled="promptPagination.page === promptPagination.pages" @click="applyPromptFilters(promptPagination.page + 1)">下一頁</button>
      </div>
    </div>

    <!-- 提示詞知識庫管理頁面 -->
    <div v-else-if="currentTab === 'prompt-kb'" class="admin-content card">
      <div class="toolbar">
        <div class="search-box">
          <span class="icon">🔍</span>
          <input v-model="promptKbSearchQuery" placeholder="搜尋提示詞標題或內容..." @input="fetchPromptKb" />
        </div>
        <div class="toolbar-actions">
          <button class="btn-primary" @click="classifyAllPromptKb" :disabled="classifyingPromptKb">
            <span v-if="classifyingPromptKb">處理中...</span>
            <span v-else>✨ AI 批次自動標籤</span>
          </button>
          <button class="btn-ghost" @click="fetchPromptKb">刷新清單</button>
        </div>
      </div>

      <div class="table-container">
        <table class="admin-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>標題 (Title)</th>
              <th>標籤 (Tags)</th>
              <th>狀態</th>
              <th>建立時間</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in promptKbEntries" :key="entry.id">
              <td>#{{ entry.id }}</td>
              <td><strong>{{ entry.title }}</strong></td>
              <td>
                <span v-for="tag in entry.tags" :key="tag" class="category-badge" style="margin-right:0.25rem;">{{ tag }}</span>
              </td>
              <td>
                <span :class="entry.is_public ? 'badge-success' : 'badge-danger'" style="padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; background: rgba(56, 189, 248, 0.1); color: #38bdf8;">
                  {{ entry.is_public ? '公開' : '隱藏' }}
                </span>
              </td>
              <td>{{ new Date(entry.created_at).toLocaleDateString() }}</td>
              <td class="actions">
                <button class="btn-action edit" @click="editPromptKb(entry)">編輯</button>
                <button class="btn-action delete" @click="deletePromptKb(entry)">刪除</button>
              </td>
            </tr>
            <tr v-if="promptKbEntries.length === 0" class="empty-row">
              <td colspan="6">尚無任何提示詞知識庫資料</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 提示詞知識庫編輯 Modal -->
    <Teleport to="body">
      <div v-if="editingPromptKb" class="modal-overlay" @click.self="cancelEditPromptKb">
        <div class="modal-card card shadow-lg">
          <div class="modal-header">
            <h3>編輯提示詞知識庫：{{ editingPromptKb.title }}</h3>
          </div>
          
          <div class="modal-body">
            <div class="form-group mb-4">
              <label class="form-label">標題 <span class="required">*</span></label>
              <input v-model="promptKbForm.title" class="form-input" placeholder="名稱" />
            </div>
            <div class="form-group mb-4">
              <label class="form-label">描述</label>
              <textarea v-model="promptKbForm.description" rows="2" class="form-input" placeholder="簡短描述..."></textarea>
            </div>
            <div class="form-group mb-4">
              <label class="form-label">標籤 (Tags)</label>
              <input v-model="promptKbForm.tagsInput" class="form-input" placeholder="多個以逗號隔開" />
            </div>
            <div class="form-group mb-4">
              <label class="form-label">完整內容 <span class="required">*</span></label>
              <textarea v-model="promptKbForm.prompt_content" rows="6" class="form-input" placeholder="Prompt 內容..."></textarea>
            </div>
            <div class="form-group" style="display:flex; align-items:center;">
              <input type="checkbox" id="kb-public" v-model="promptKbForm.is_public" style="margin-right: 0.5rem;">
              <label class="form-label" for="kb-public" style="margin-bottom: 0;">公開分享 (設為隱藏則前台不可見)</label>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-ghost" @click="cancelEditPromptKb">取消</button>
            <button class="btn-primary" @click="savePromptKbEdit" :disabled="saving || !promptKbForm.title || !promptKbForm.prompt_content">
              {{ saving ? '儲存中...' : '儲存修改' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 技能編輯 Modal -->
    <Teleport to="body">
      <div v-if="editingSkill" class="modal-overlay" @click.self="cancelEdit">
        <div class="modal-card card shadow-lg">
          <div class="modal-header">
            <h3>編輯技能：{{ editingSkill.name }}</h3>
          </div>
          
          <div class="modal-body">
            <div class="form-group mb-4">
              <label class="form-label">技能名稱</label>
              <input v-model="editForm.name" class="form-input" placeholder="技能名稱" />
            </div>
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
    </Teleport>


    <!-- MCP 編輯 Modal -->
    <Teleport to="body">
      <div v-if="editingMcp" class="modal-overlay" @click.self="cancelEditMcp">
        <div class="modal-card card shadow-lg">
          <div class="modal-header">
            <h3>編輯 MCP Server：{{ editingMcp.display_name || editingMcp.name }}</h3>
          </div>
          
          <div class="modal-body">
            <div class="form-group mb-4">
              <label class="form-label">識別標籤 (Name)</label>
              <input v-model="mcpForm.name" class="form-input" placeholder="例如: github-mcp" />
            </div>
            <div class="form-group mb-4">
              <label class="form-label">顯示名稱 (Display Name)</label>
              <input v-model="mcpForm.display_name" class="form-input" placeholder="例如: GitHub 整合服務" />
            </div>
            <div class="form-group mb-4">
              <label class="form-label">描述</label>
              <textarea v-model="mcpForm.description" rows="3" class="form-input" placeholder="輸入 MCP 描述..."></textarea>
            </div>
            <div class="form-group mb-4">
              <label class="form-label">作者</label>
              <input v-model="mcpForm.author" class="form-input" placeholder="作者名稱" />
            </div>
            <div class="form-group mb-4">
              <label class="form-label">標籤 (以逗號分隔)</label>
              <input v-model="mcpForm.tagsString" class="form-input" placeholder="例如: github, git, tools" />
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-ghost" @click="cancelEditMcp">取消</button>
            <button class="btn-primary" @click="saveMcpEdit" :disabled="saving">
              {{ saving ? '儲存中...' : '儲存修改' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 使用者編輯/新增 Modal -->
    <Teleport to="body">
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
              <label class="form-label">密碼 {{ isCreatingUser ? '(必填)' : '(留空則不修改)' }}</label>
              <input v-model="userForm.password" type="password" class="form-input" placeholder="輸入密碼..." />
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
    </Teleport>

    <!-- Docker Repo 編輯/新增 Modal -->
    <Teleport to="body">
      <div v-if="editingDockerRepo || isCreatingDockerRepo" class="modal-overlay" @click.self="cancelEditDockerRepo">
        <div class="modal-card card shadow-lg">
          <div class="modal-header">
            <h3>{{ isCreatingDockerRepo ? '新增 Docker 倉庫' : '編輯倉庫：' + editingDockerRepo.name }}</h3>
          </div>
          
          <div class="modal-body">
            <div class="form-group mb-4">
              <label class="form-label">倉庫名稱 (Repository Name)</label>
              <input v-model="dockerRepoForm.name" class="form-input" placeholder="例如: my-team/backend" :disabled="!isCreatingDockerRepo" />
              <span v-if="isCreatingDockerRepo" class="text-xs text-muted" style="margin-top:0.3rem">建立後不可修改。這必須與你執行 `docker push` 時的名稱一致。</span>
            </div>
            <div class="form-group mb-4">
              <label class="form-label">倉庫描述 (Description)</label>
              <textarea v-model="dockerRepoForm.description" rows="3" class="form-input" placeholder="輸入倉庫的功能或用途..."></textarea>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-ghost" @click="cancelEditDockerRepo">取消</button>
            <button class="btn-primary" @click="saveDockerRepoEdit" :disabled="saving">
              {{ saving ? '處理中...' : (isCreatingDockerRepo ? '確認建立' : '確認修改') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- NPM 倉庫 編輯/新增 Modal -->
    <Teleport to="body">
      <div v-if="editingNpmPackage || isCreatingNpmPackage" class="modal-overlay" @click.self="cancelEditNpmPackage">
        <div class="modal-card card shadow-lg">
          <div class="modal-header">
            <h3>{{ isCreatingNpmPackage ? '新增 NPM 套件' : '編輯套件：' + editingNpmPackage.name }}</h3>
          </div>
          
          <div class="modal-body">
            <div class="form-group mb-4">
              <label class="form-label">套件名稱 (Package Name)</label>
              <input v-model="npmPackageForm.name" class="form-input" placeholder="例如: my-team/backend" :disabled="!isCreatingNpmPackage" />
              <span v-if="isCreatingNpmPackage" class="text-xs text-muted" style="margin-top:0.3rem">建立後不可修改。這必須與你執行 `npm publish` 時的名稱一致。</span>
            </div>
            <div class="form-group mb-4">
              <label class="form-label">套件描述 (Description)</label>
              <textarea v-model="npmPackageForm.description" rows="3" class="form-input" placeholder="輸入套件的功能或用途..."></textarea>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-ghost" @click="cancelEditNpmPackage">取消</button>
            <button class="btn-primary" @click="saveNpmPackageEdit" :disabled="saving">
              {{ saving ? '處理中...' : (isCreatingNpmPackage ? '確認建立' : '確認修改') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
    <!-- Prompt Setting 編輯/新增 Modal -->
    <Teleport to="body">
      <div v-if="editingPrompt || isCreatingPrompt" class="modal-overlay" @click.self="cancelEditPrompt">
        <div class="modal-card card shadow-lg">
          <div class="modal-header">
            <h3>{{ isCreatingPrompt ? '新增提示詞設定' : '編輯設定：' + editingPrompt.name }}</h3>
          </div>
          
          <div class="modal-body">
            <div class="form-group mb-4">
              <label class="form-label">分類 (Category)</label>
              <select v-model="promptForm.category" class="form-input">
                <option v-for="cat in promptCategories.filter(c => c.value !== '')" :key="cat.value" :value="cat.value">{{ cat.label }}</option>
              </select>
            </div>
            <div class="form-group mb-4">
              <label class="form-label">內容名稱 (Name)</label>
              <input v-model="promptForm.name" class="form-input" placeholder="例如: 客觀冷靜" />
            </div>
            <div class="form-group mb-4" v-if="promptForm.category === 'role' || promptForm.category === 'scenario'">
              <label class="form-label">選項群組名稱 (Group Name, 選擇性)</label>
              <input v-model="promptForm.group_name" class="form-input" placeholder="例如: 技術與開發" />
            </div>
            <div class="form-group mb-4">
              <label class="form-label">排序權重 (Order Index)</label>
              <input type="number" v-model="promptForm.order_index" class="form-input" placeholder="0" />
            </div>
            <div class="form-group mb-4">
              <label class="form-label">啟用狀態 (Is Active)</label>
              <label class="form-switch" style="display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem;">
                <input type="checkbox" v-model="promptForm.is_active" />
                <span>啟用此設定項目就在前端顯示</span>
              </label>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn-ghost" @click="cancelEditPrompt">取消</button>
            <button class="btn-primary" @click="savePromptEdit" :disabled="saving">
              {{ saving ? '處理中...' : (isCreatingPrompt ? '確認建立' : '確認修改') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
const currentTab = ref('skills')
const isSidebarCollapsed = ref(false)
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
const dockerPerPage = ref(10)

// 分頁狀態
const skillPagination = reactive({ page: 1, total: 0, pages: 1 })
const skillSortField = ref('name')
const skillSortOrder = ref('asc')
const userPagination = reactive({ page: 1, total: 0, pages: 1 })
const dockerPagination = reactive({ page: 1, total: 0, pages: 1 })
const npmPagination = reactive({ page: 1, total: 0, pages: 1 })
const npmSortField = ref('created_at')
const npmSortOrder = ref('desc')

// Docker 倉庫狀態
const dockerRepos = ref([])
const dockerSearchQuery = ref('')
const editingDockerRepo = ref(null)
const isCreatingDockerRepo = ref(false)
const dockerRepoForm = reactive({ name: '', description: '' })

// NPM 套件狀態
const npmPackages = ref([])
const npmSearchQuery = ref('')
const editingNpmPackage = ref(null)
const isCreatingNpmPackage = ref(false)
const npmPackageForm = reactive({ name: '', description: '' })
const npmPerPage = ref(10)

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
const editForm = ref({ name: '', description: '', author: '', tagsString: '' })

const editingUser = ref(null)
const isCreatingUser = ref(false)
const userForm = reactive({ username: '', email: '', password: '', role: 'user', permissions: [] })
const ALL_PERMISSIONS = ['skill:create', 'skill:update', 'skill:delete', 'admin:access']

const saving = ref(false)

// 提示詞管理狀態與操作
const allPrompts = ref([])
const prompts = ref([])
const promptSearchQuery = ref('')
const promptCategoryFilter = ref('')
const promptSortField = ref('order_index')
const promptSortOrder = ref('asc')
const promptPagination = reactive({ page: 1, total: 0, pages: 1 })
const promptPerPage = ref(10)

const editingPrompt = ref(null)
const isCreatingPrompt = ref(false)
const promptForm = reactive({ category: 'scenario', name: '', group_name: '', order_index: 0, content: '', is_active: true })

// 提示詞知識庫管理狀態與操作
const promptKbEntries = ref([])
const promptKbSearchQuery = ref('')
const editingPromptKb = ref(null)
const promptKbForm = reactive({ title: '', description: '', tagsInput: '', prompt_content: '', is_public: true })
const classifyingPromptKb = ref(false)

const promptCategories = [
  { value: '', label: '全部' },
  { value: 'scenario', label: '任務類型' },
  { value: 'role', label: '扮演角色' },
  { value: 'format', label: '回覆格式' },
  { value: 'tone', label: '語氣與風格' },
  { value: 'constraint', label: '限制與要求' },
]

async function fetchPrompts(page = 1) {
  try {
    const res = await fetch(`/api/admin/prompt-settings`, {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (res.ok) {
        allPrompts.value = await res.json()
        applyPromptFilters(page)
    }
  } catch (e) {
    console.error('Fetch prompts error:', e)
  }
}

function applyPromptFilters(page = 1) {
  promptPagination.page = page
  let filtered = allPrompts.value

  if (promptCategoryFilter.value) {
    filtered = filtered.filter(p => p.category === promptCategoryFilter.value)
  }

  if (promptSearchQuery.value) {
    const q = promptSearchQuery.value.toLowerCase()
    filtered = filtered.filter(p => 
      p.name.toLowerCase().includes(q) || 
      (p.content && p.content.toLowerCase().includes(q)) ||
      (p.group_name && p.group_name.toLowerCase().includes(q))
    )
  }

  filtered.sort((a, b) => {
    let valA = a[promptSortField.value]
    let valB = b[promptSortField.value]
    
    if (typeof valA === 'string') valA = valA.toLowerCase()
    if (typeof valB === 'string') valB = valB.toLowerCase()

    if (valA < valB) return promptSortOrder.value === 'asc' ? -1 : 1
    if (valA > valB) return promptSortOrder.value === 'asc' ? 1 : -1
    return 0
  })

  promptPagination.total = filtered.length
  promptPagination.pages = Math.ceil(filtered.length / promptPerPage.value) || 1
  
  if (promptPagination.page > promptPagination.pages) {
    promptPagination.page = promptPagination.pages
  }

  const start = (promptPagination.page - 1) * promptPerPage.value
  const end = start + promptPerPage.value
  prompts.value = filtered.slice(start, end)
}

let promptTimeout = null
function debouncedFetchPrompts() {
  clearTimeout(promptTimeout)
  promptTimeout = setTimeout(() => applyPromptFilters(1), 300)
}

function sortPrompts(field) {
  if (promptSortField.value === field) {
    promptSortOrder.value = promptSortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    promptSortField.value = field
    promptSortOrder.value = 'asc'
  }
  applyPromptFilters(1)
}

function createPrompt() {
  isCreatingPrompt.value = true
  editingPrompt.value = null
  promptForm.category = promptCategoryFilter.value || 'scenario'
  promptForm.name = ''
  promptForm.group_name = ''
  promptForm.order_index = 0
  promptForm.content = ''
  promptForm.is_active = true
}

function editPrompt(prompt) {
  isCreatingPrompt.value = false
  editingPrompt.value = prompt
  promptForm.category = prompt.category
  promptForm.name = prompt.name
  promptForm.group_name = prompt.group_name || ''
  promptForm.order_index = prompt.order_index || 0
  promptForm.content = prompt.content || ''
  promptForm.is_active = prompt.is_active !== false
}

function cancelEditPrompt() {
  editingPrompt.value = null
  isCreatingPrompt.value = false
}

async function savePromptEdit() {
  saving.value = true
  try {
    const isNew = isCreatingPrompt.value
    const url = isNew ? '/api/admin/prompt-settings' : `/api/admin/prompt-settings/${editingPrompt.value.id}`
    const method = isNew ? 'POST' : 'PUT'
    
    // 轉型
    const payload = { ...promptForm, order_index: parseInt(promptForm.order_index) }

    const res = await fetch(url, {
      method: method,
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify(payload)
    })
    
    if (res.ok) {
      await fetchPrompts()
      cancelEditPrompt()
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

async function deletePrompt(prompt) {
  if (!confirm(`確定要刪除設定 "${prompt.name}" 嗎？`)) return
  try {
    const res = await fetch(`/api/admin/prompt-settings/${prompt.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (res.ok) fetchPrompts()
  } catch (e) {
    alert('刪除失敗')
  }
}

async function fetchPromptKb() {
  try {
    const res = await fetch('/api/admin/prompt-knowledge', {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (res.ok) {
        let data = await res.json()
        if (promptKbSearchQuery.value) {
           const q = promptKbSearchQuery.value.toLowerCase()
           data = data.filter(e => e.title.toLowerCase().includes(q) || e.prompt_content.toLowerCase().includes(q))
        }
        promptKbEntries.value = data
    }
  } catch (e) {
    console.error('Fetch prompt knowledge error:', e)
  }
}

async function classifyAllPromptKb() {
  if (!confirm('將使用 AI 自動分析所有知識庫文章並加上特徵標籤，是否繼續？')) return
  classifyingPromptKb.value = true
  try {
    const res = await fetch('/api/admin/prompt-knowledge/classify-all', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      const data = await res.json()
      alert(`分類完成！成功為 ${data.classified} 筆知識庫加上新標籤，跳過 ${data.skipped} 筆已具備完整標籤的項目。`)
      await fetchPromptKb()
    } else {
      const err = await res.json()
      alert(err.message || '自動標籤失敗')
    }
  } catch (e) {
    alert('自動標籤失敗')
  } finally {
    classifyingPromptKb.value = false
  }
}

function editPromptKb(entry) {
  editingPromptKb.value = entry
  promptKbForm.title = entry.title
  promptKbForm.description = entry.description || ''
  promptKbForm.tagsInput = (entry.tags || []).join(', ')
  promptKbForm.prompt_content = entry.prompt_content
  promptKbForm.is_public = entry.is_public
}

function cancelEditPromptKb() {
  editingPromptKb.value = null
}

async function savePromptKbEdit() {
  saving.value = true
  try {
    const payload = {
      title: promptKbForm.title,
      description: promptKbForm.description,
      tags: promptKbForm.tagsInput.split(',').map(t => t.trim()).filter(Boolean),
      prompt_content: promptKbForm.prompt_content,
      is_public: promptKbForm.is_public
    }

    const res = await fetch(`/api/admin/prompt-knowledge/${editingPromptKb.value.id}`, {
      method: 'PUT',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify(payload)
    })
    
    if (res.ok) {
      await fetchPromptKb()
      cancelEditPromptKb()
    } else {
      alert('儲存失敗')
    }
  } catch (e) {
    alert('操作失敗')
  } finally {
    saving.value = false
  }
}

async function deletePromptKb(entry) {
  if (!confirm(`確定要刪除設定 "${entry.title}" 嗎？`)) return
  try {
    const res = await fetch(`/api/admin/prompt-knowledge/${entry.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (res.ok) fetchPromptKb()
  } catch (e) {
    alert('刪除失敗')
  }
}

async function fetchData(page = 1) {
  skillPagination.page = page
  try {
    const headers = { 'Authorization': `Bearer ${authStore.token}` }
    const params = new URLSearchParams({
      q: searchQuery.value,
      page: page,
      per_page: skillPerPage.value,
      sort: skillSortField.value,
      order: skillSortOrder.value
    })
    const [skillsRes, statsRes] = await Promise.all([
      fetch(`/api/admin/skills?${params.toString()}`, { headers }),
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

function sortSkills(field) {
  if (skillSortField.value === field) {
    skillSortOrder.value = skillSortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    skillSortField.value = field
    skillSortOrder.value = 'asc'
  }
  fetchData(1)
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

async function fetchDockerRepos(page = 1) {
  dockerPagination.page = page
  try {
    const res = await fetch(`/api/admin/docker-repos?q=${dockerSearchQuery.value}&page=${page}&per_page=${dockerPerPage.value}`, {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (res.ok) {
        const data = await res.json()
        dockerRepos.value = data.repositories || []
        dockerPagination.total = data.total
        dockerPagination.pages = data.pages
    }
  } catch (e) {
    console.error('Failed to fetch docker repos', e)
  }
}

async function fetchNpmPackages(page = 1) {
  npmPagination.page = page
  try {
    const res = await fetch(`/api/admin/npm-packages?q=${npmSearchQuery.value}&page=${page}&per_page=${npmPerPage.value}`, {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (res.ok) {
        const data = await res.json()
        npmPackages.value = data.packages || []
        npmPagination.total = data.total
        npmPagination.pages = data.pages
    }
  } catch (e) {
    console.error('Failed to fetch npm packages', e)
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
  else if (newTab === 'docker') fetchDockerRepos()
  else if (newTab === 'npm') fetchNpmPackages()
  else if (newTab === 'prompts') fetchPrompts()
  else if (newTab === 'prompt-kb') fetchPromptKb()
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

let dockerTimeout = null
function debouncedFetchDockerRepos() {
  clearTimeout(dockerTimeout)
  dockerTimeout = setTimeout(() => fetchDockerRepos(1), 300)
}

let npmTimeout = null
function debouncedFetchNpmPackages() {
  clearTimeout(npmTimeout)
  npmTimeout = setTimeout(() => fetchNpmPackages(1), 300)
}

// 技能操作
function editSkill(skill) {
  editingSkill.value = skill
  editForm.value = {
    name: skill.name,
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
      name: editForm.value.name,
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
const mcpForm = ref({ name: '', display_name: '', description: '', author: '', tagsString: '' })

function editMcp(mcp) {
  editingMcp.value = mcp
  mcpForm.value = {
    name: mcp.name,
    display_name: mcp.display_name,
    description: mcp.description,
    author: mcp.author,
    tagsString: (mcp.tags || []).join(', ')
  }
}

function cancelEditMcp() { editingMcp.value = null }

async function saveMcpEdit() {
  saving.value = true
  try {
    const payload = {
      name: mcpForm.value.name,
      display_name: mcpForm.value.display_name,
      description: mcpForm.value.description,
      author: mcpForm.value.author,
      tags: mcpForm.value.tagsString.split(',').map(t => t.trim()).filter(Boolean)
    }
    const res = await fetch(`/api/admin/mcps/${editingMcp.value.name}`, {
      method: 'PATCH',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify(payload)
    })
    if (res.ok) {
      await fetchMcps(mcpPagination.page)
      cancelEditMcp()
    } else {
      alert('儲存失敗')
    }
  } catch (e) {
    alert('儲存失敗')
  } finally {
    saving.value = false
  }
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
  editingUser.value = null
  userForm.username = ''
  userForm.email = ''
  userForm.password = ''
  userForm.role = 'user'
  userForm.permissions = []
  isCreatingUser.value = true
}

function editUser(user) {
  isCreatingUser.value = false
  editingUser.value = user
  userForm.username = user.username
  userForm.email = user.email
  userForm.password = ''
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
    
    const payload = { ...userForm }
    // 如果是編輯模式且密碼為空，則移除密碼欄位以防後端報錯或誤改
    if (!isNew && !payload.password) {
      delete payload.password
    }

    const res = await fetch(url, {
      method: method,
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify(payload)
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

// Docker Repo 操作
function createDockerRepo() {
  isCreatingDockerRepo.value = true
  editingDockerRepo.value = null
  dockerRepoForm.name = ''
  dockerRepoForm.description = ''
}

function editDockerRepo(repo) {
  isCreatingDockerRepo.value = false
  editingDockerRepo.value = repo
  dockerRepoForm.name = repo.name
  dockerRepoForm.description = repo.description || ''
}

function cancelEditDockerRepo() { 
  editingDockerRepo.value = null
  isCreatingDockerRepo.value = false
}

async function saveDockerRepoEdit() {
  saving.value = true
  try {
    const isNew = isCreatingDockerRepo.value
    const url = isNew ? '/api/admin/docker-repos' : `/api/admin/docker-repos/${editingDockerRepo.value.id}`
    const method = isNew ? 'POST' : 'PATCH'
    
    // 如果是更新，把不必要的 name 拿掉（以防後端報錯，雖然設定檔沒檢查也無妨）
    const payload = isNew ? { name: dockerRepoForm.name, description: dockerRepoForm.description } : { description: dockerRepoForm.description }

    const res = await fetch(url, {
      method: method,
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify(payload)
    })
    
    if (res.ok) {
      await fetchDockerRepos(dockerPagination.page)
      cancelEditDockerRepo()
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

async function deleteDockerRepo(repo) {
  if (!confirm(`確定要刪除 Docker 倉庫 "${repo.name}" 嗎？\n注意：這將連同 Registry 中的實際 Image 資料一併刪除，此操作不可還原。`)) return
  try {
    const res = await fetch(`/api/admin/docker-repos/${repo.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (res.ok) fetchDockerRepos(dockerPagination.page)
  } catch (e) {
    alert('刪除失敗')
  }
}

// NPM Repo 操作
function createNpmPackage() {
  isCreatingNpmPackage.value = true
  editingNpmPackage.value = null
  npmPackageForm.name = ''
  npmPackageForm.description = ''
}

function editNpmPackage(pkg) {
  isCreatingNpmPackage.value = false
  editingNpmPackage.value = pkg
  npmPackageForm.name = pkg.name
  npmPackageForm.description = pkg.description || ''
}

function cancelEditNpmPackage() { 
  editingNpmPackage.value = null
  isCreatingNpmPackage.value = false
}

async function saveNpmPackageEdit() {
  saving.value = true
  try {
    const isNew = isCreatingNpmPackage.value
    const url = isNew ? '/api/admin/npm-packages' : `/api/admin/npm-packages/${editingNpmPackage.value.id}`
    const method = isNew ? 'POST' : 'PATCH'
    
    // 如果是更新，把不必要的 name 拿掉（以防後端報錯，雖然設定檔沒檢查也無妨）
    const payload = isNew ? { name: npmPackageForm.name, description: npmPackageForm.description } : { description: npmPackageForm.description }

    const res = await fetch(url, {
      method: method,
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify(payload)
    })
    
    if (res.ok) {
      await fetchNpmPackages(npmPagination.page)
      cancelEditNpmPackage()
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

async function deleteNpmPackage(pkg) {
  if (!confirm(`確定要刪除 NPM 套件 "${pkg.name}" 嗎？`)) return
  try {
    const res = await fetch(`/api/admin/npm-packages/${pkg.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    })
    if (res.ok) fetchNpmPackages(npmPagination.page)
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
  else if (currentTab.value === 'users') fetchUsers(1)
  else if (currentTab.value === 'mcps') fetchMcps(1)
  else if (currentTab.value === 'docker') fetchDockerRepos(1)
  else if (currentTab.value === 'npm') fetchNpmPackages(1)
  else if (currentTab.value === 'prompts') fetchPrompts(1)
})

watch(currentTab, (newTab) => {
  if (newTab === 'users') fetchUsers(1)
  else if (newTab === 'mcps') fetchMcps(1)
  else if (newTab === 'docker') fetchDockerRepos(1)
  else if (newTab === 'npm') fetchNpmPackages(1)
  else if (newTab === 'prompts') fetchPrompts()
  else fetchData(1)
})
</script>

<style scoped>
/* ── Refined Industrial Admin Dashboard ── */
/* ── Admin Sidebar Layout ── */
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'DM Sans', 'Inter', system-ui, sans-serif;
}

.admin-sidebar {
  width: 260px;
  background: #0d1117;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  z-index: 100;
  flex-shrink: 0;
  height: 100vh;
  position: sticky;
  top: 0;
}

.admin-sidebar.collapsed {
  width: 72px;
}

.sidebar-header {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}

.sidebar-header .logo {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  overflow: hidden;
}

.logo-text {
  font-weight: 700;
  font-size: 1rem;
  color: #fff;
  white-space: nowrap;
}

.hamburger-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  margin-left: auto;
}

.hamburger-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.sidebar-nav {
  padding: 1.5rem 0.6rem;
  flex: 1;
  overflow-y: auto;
}

/* Scrollbar styling for sidebar */
.sidebar-nav::-webkit-scrollbar { width: 4px; }
.sidebar-nav::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }

.nav-group {
  margin-bottom: 2rem;
}

.group-title {
  font-size: 0.75rem;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 700;
  letter-spacing: 0.1em;
  padding: 0 1rem 0.8rem;
  opacity: 0.6;
}

.sidebar-nav button {
  width: 100%;
  padding: 0.85rem 1rem;
  display: flex;
  align-items: center;
  gap: 1.1rem;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 4px;
  position: relative;
}

.sidebar-nav button:hover {
  background: rgba(255, 255, 255, 0.04);
  color: #fff;
}

.sidebar-nav button.active {
  background: rgba(37, 164, 100, 0.1);
  color: var(--accent);
  font-weight: 600;
}

.sidebar-nav button.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 20%;
  height: 60%;
  width: 3px;
  background: var(--accent);
  border-radius: 0 4px 4px 0;
}

.sidebar-nav button .icon {
  font-size: 1.25rem;
  flex-shrink: 0;
  width: 24px;
  text-align: center;
}

.sidebar-nav button .label {
  white-space: nowrap;
  font-size: 0.95rem;
}

.admin-sidebar.collapsed .sidebar-nav button {
  justify-content: center;
  padding: 0.85rem 0;
}

.admin-main {
  flex: 1;
  min-width: 0;
  overflow-x: hidden;
}

.admin-page-inner {
  padding: 2.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* Header & Typography */
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  position: relative;
}

.admin-header::before {
  content: '';
  position: absolute;
  top: -50px;
  left: -50px;
  right: -50px;
  bottom: 0;
  background: radial-gradient(circle at top left, rgba(37, 164, 100, 0.04), transparent 50%);
  pointer-events: none;
  z-index: -1;
}

.header-content h1 {
  font-size: 2.2rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 0.4rem 0;
  color: #fff;
}

.subtitle {
  color: var(--text-muted);
  font-size: 0.95rem;
  font-weight: 500;
  margin: 0;
  letter-spacing: 0.01em;
}

/* Stats Precision Instruments */
.stats-cards {
  display: flex;
  gap: 1.2rem;
}

.stat-card {
  background: rgba(22, 27, 34, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 1.2rem 1.5rem;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  min-width: 140px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.stat-card::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 2px;
  background: var(--accent);
  opacity: 0.7;
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600;
  margin-bottom: 0.4rem;
}

.stat-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.8rem;
  font-weight: 400;
  color: #fff;
  line-height: 1;
}

/* Editorial Tabs Navigation */
.tabs-nav {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding-bottom: 0;
}

.tabs-nav button {
  padding: 0 0 1rem 0;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-weight: 500;
  font-size: 0.95rem;
  cursor: pointer;
  transition: color 0.2s ease;
  position: relative;
}

.tabs-nav button:hover {
  color: var(--text-primary);
}

.tabs-nav button.active {
  color: #fff;
  font-weight: 600;
}

.tabs-nav button::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 100%;
  height: 2px;
  background: var(--accent);
  transform: scaleX(0);
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: left right;
}

.tabs-nav button.active::after {
  transform: scaleX(1);
}

/* Main Content Area */
.admin-content {
  padding: 2rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: visible;
}

/* Toolbar & Search */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.toolbar-right, .toolbar-actions {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-shrink: 0;
}

.search-box {
  flex: 1;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 0 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  transition: all 0.2s ease;
}

.search-box:focus-within {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 0 3px var(--accent-dim);
}

.search-box .icon {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.search-box input {
  background: transparent;
  border: none;
  color: #fff;
  padding: 0.75rem 0;
  width: 100%;
  outline: none;
  font-size: 0.9rem;
  font-weight: 400;
}
.search-box input::placeholder {
  color: var(--text-muted);
}

/* Per Page Dropdown & View Toggles */
.per-page-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.per-page-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 500;
}
.per-page-select {
  padding: 0.4rem 2rem 0.4rem 0.8rem;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.03) url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20width%3D%2212%22%20height%3D%2212%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%238b949e%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E') no-repeat right 0.5rem center;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--text-primary);
  font-size: 0.85rem;
  outline: none;
  cursor: pointer;
  appearance: none;
  font-weight: 500;
  transition: all 0.2s ease;
}
.per-page-select:focus { border-color: var(--accent); }

.view-toggle {
  display: flex;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  padding: 2px;
}
.view-btn {
  padding: 0.4rem 0.6rem;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.15s ease;
}
.view-btn:hover { color: var(--text-primary); }
.view-btn.active { background: rgba(255, 255, 255, 0.1); color: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }

/* Buttons Enhancement */
.btn-primary {
  background: linear-gradient(180deg, var(--accent) 0%, #1e8751 100%);
  border: 1px solid #28b86f;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.2), 0 2px 4px rgba(0,0,0,0.2);
  color: #fff;
  font-weight: 600;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  transition: all 0.15s ease;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.btn-primary:hover:not(:disabled) {
  background: linear-gradient(180deg, #28b86f 0%, #20965a 100%);
  transform: translateY(-1px);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.2), 0 4px 8px rgba(0,0,0,0.3);
}
.btn-primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
}

.btn-ghost {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: var(--text-primary);
  font-weight: 500;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  transition: all 0.15s ease;
  cursor: pointer;
}
.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.3);
}

.btn-ai-classify {
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  border: 1px solid rgba(37, 164, 100, 0.4);
  background: rgba(37, 164, 100, 0.08);
  color: var(--accent);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}
.btn-ai-classify:hover:not(:disabled) {
  background: rgba(37, 164, 100, 0.15);
  border-color: var(--accent);
}

/* Batch Operations Bar */
.batch-bar {
  background: rgba(30, 41, 59, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(148, 163, 184, 0.1);
  padding: 0.75rem 1.2rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  animation: fadeUp 0.2s ease-out;
}
.batch-info { color: #e2e8f0; font-size: 0.9rem; }
.btn-select-all { background: transparent; border: 1px solid rgba(255,255,255,0.2); color: #cbd5e1; padding: 0.3rem 0.8rem; border-radius: 4px; font-size: 0.8rem; cursor: pointer; transition: background 0.15s; }
.btn-select-all:hover { background: rgba(255,255,255,0.05); }
.btn-batch-delete { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); color: #f87171; padding: 0.3rem 0.8rem; border-radius: 4px; font-size: 0.8rem; cursor: pointer; font-weight: 600; transition: all 0.15s; }
.btn-batch-delete:hover:not(:disabled) { background: rgba(239, 68, 68, 0.2); color: #fca5a5; }
.btn-batch-cancel { background: transparent; border: none; color: var(--text-muted); font-size: 0.85rem; cursor: pointer; margin-left: auto; }
.btn-batch-cancel:hover { color: #fff; text-decoration: underline; }

/* Data Tables */
.table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(13, 17, 23, 0.4);
}
.admin-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  text-align: left;
}
.admin-table th {
  padding: 1rem 1.2rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(255, 255, 255, 0.02);
  white-space: nowrap;
}
.admin-table td {
  padding: 1.2rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
  font-size: 0.9rem;
  vertical-align: middle;
  transition: background 0.15s ease;
}
.admin-table tbody tr:hover td {
  background: rgba(255, 255, 255, 0.04) !important;
}
.admin-table tbody tr:last-child td {
  border-bottom: none;
}
.admin-table tbody tr.row-selected td {
  background: rgba(37, 164, 100, 0.08);
}
.admin-table tbody tr.row-selected td:first-child {
  border-left: 3px solid var(--accent);
}

.sortable { cursor: pointer; user-select: none; transition: background 0.2s; }
.sortable:hover { background: rgba(255,255,255,0.05); color: #fff; }
.sort-icon { font-size: 0.7rem; margin-left: 0.4rem; opacity: 0.5; }

.badge-active { padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; background: rgba(37, 164, 100, 0.1); color: var(--accent); border: 1px solid rgba(37, 164, 100, 0.2); }
.badge-inactive { padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2); }

.category-badge {
  background: rgba(56, 189, 248, 0.1);
  color: #38bdf8;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  border: 1px solid rgba(56, 189, 248, 0.2);
}

/* Skill Name Layout */
.skill-name-cell {
  position: relative;
}
.skill-name {
  font-weight: 600;
  color: var(--text-primary);
  display: inline-block;
  vertical-align: middle;
}

/* List Elements that were acting like blocks */
.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

/* Actions Column */
.actions-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  justify-content: flex-start;
}

/* Custom Checkbox */
.cb-col { width: 40px; text-align: center; }
.batch-cb {
  appearance: none;
  width: 16px;
  height: 16px;
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 4px;
  background: transparent;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}
.batch-cb:checked {
  background: var(--accent);
  border-color: var(--accent);
}
.batch-cb:checked::after {
  content: '';
  position: absolute;
  left: 4px;
  top: 1px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

/* Specific Cell Styling */
.skill-name-cell .skill-name {
  font-weight: 600;
  color: #fff;
}
.category-select {
  padding: 0.35rem 0.6rem;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.03) url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20width%3D%2212%22%20height%3D%2212%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%238b949e%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C%2Fpolyline%3E%3C%2Fsvg%3E') no-repeat right 0.5rem center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  font-size: 0.85rem;
  appearance: none;
  cursor: pointer;
  min-width: 130px;
}
.category-select:focus { border-color: var(--accent); }

.tag-row { flex-wrap: wrap; gap: 0.4rem; }
.tag {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}
code {
  font-family: 'JetBrains Mono', monospace;
  background: rgba(255,255,255,0.05);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 0.8rem;
  color: var(--text-primary);
}

/* Action Buttons */
.actions { display: flex; gap: 0.5rem; }
.btn-action {
  background: transparent;
  border: none;
  padding: 0.4rem 0.6rem;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.15s ease;
}
.btn-action.edit { color: #60a5fa; }
.btn-action.edit:hover { background: rgba(96, 165, 250, 0.1); }
.btn-action.delete { color: #f87171; }
.btn-action.delete:hover { background: rgba(248, 113, 113, 0.1); }

/* Grid Cards (Skills & MCPs) */
.skill-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.2rem;
  margin-top: 1rem;
}

.skill-card-admin {
  background: rgba(22, 27, 34, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.skill-card-admin:hover {
  background: rgba(22, 27, 34, 0.8);
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
  transform: translateY(-2px);
}
.card-head { display: flex; align-items: center; gap: 0.8rem; }
.card-icon { font-size: 1.6rem; }
.card-meta { flex: 1; min-width: 0; }
.card-name { font-weight: 600; color: #fff; font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.card-author { color: var(--text-muted); font-size: 0.8rem; margin-top: 2px;}
.card-version { font-size: 0.75rem; color: var(--accent); background: var(--accent-dim); padding: 2px 6px; border-radius: 4px;}
.card-tags { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0.4rem 0; min-height: 22px;}
.no-tag { font-size: 0.8rem; color: var(--text-muted); font-style: italic; }
.card-stats { color: var(--text-secondary); font-size: 0.85rem; font-weight: 500; margin-top: auto; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.6rem;}
.card-actions { display: flex; gap: 0.8rem; margin-top: 0.2rem;  }

/* Role & Transport Badges */
.role-badge, .transport-badge {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}
.role-badge.admin { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); }
.role-badge.maintainer { background: rgba(56, 189, 248, 0.15); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.3); }
.role-badge.user { background: rgba(148, 163, 184, 0.15); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.3); }
.transport-badge.stdio { background: rgba(245, 158, 11, 0.15); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.3); }
.transport-badge.sse { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1.5rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255,255,255,0.05);
}
.pagination button {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: var(--text-primary);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.85rem;
  transition: all 0.15s ease;
}
.pagination button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255,255,255,0.2);
}
.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.page-info {
  color: var(--text-muted);
  font-size: 0.85rem;
  font-weight: 500;
}

/* Modal Overlay & Card (Glassmorphism) */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.15s ease-out;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-card {
  background: #161b22;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  padding: 2rem;
  box-shadow: 0 24px 48px rgba(0,0,0,0.4);
  animation: slideUp 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.modal-header h3 {
  margin: 0 0 1.5rem 0;
  color: #fff;
  font-size: 1.25rem;
  font-weight: 600;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  padding-bottom: 0.8rem;
}

.form-group { margin-bottom: 1.2rem; }
.form-label {
  display: block;
  margin-bottom: 0.4rem;
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
}
.form-input, .custom-select {
  width: 100%;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  font-family: inherit;
  transition: all 0.2s ease;
}
.form-input:focus, .custom-select:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-dim);
}
.form-input:disabled { opacity: 0.6; cursor: not-allowed; }

.permission-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.8rem;
  background: rgba(255,255,255,0.02);
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.05);
}
.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #e2e8f0;
  font-size: 0.85rem;
  cursor: pointer;
}
.checkbox-item input { accent-color: var(--accent); }

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255,255,255,0.05);
}

/* Animations */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp 0.45s ease both; }

/* Empty state */
.empty-row td, .cards-empty {
  text-align: center;
  color: var(--text-muted);
  padding: 4rem;
  font-size: 0.95rem;
}

/* Utility */
.mb-4 { margin-bottom: 1rem; }
.text-xs { font-size: 0.75rem; }
.text-muted { color: var(--text-muted); }

</style>

