<template>
  <header class="app-header">
    <div class="header-inner">
      <RouterLink to="/" class="logo">
        <span class="logo-icon">🧠</span>
        <span class="logo-text">AgentSkills</span>
        <span class="logo-badge">Registry</span>
      </RouterLink>

      <nav class="nav-links">
        <RouterLink to="/skills" class="nav-link" :class="{ active: $route.path.startsWith('/skills') }">
          瀏覽
        </RouterLink>
        <RouterLink v-if="authStore.hasPermission('skill:create')" to="/publish" class="nav-link" :class="{ active: $route.path === '/publish' }">
          發布
        </RouterLink>
        <RouterLink v-if="authStore.isAdmin" to="/admin" class="nav-link" :class="{ active: $route.path === '/admin' }">
          管理
        </RouterLink>
        <a href="https://github.com/agentskills/registry" target="_blank" class="nav-link">
          GitHub
        </a>
      </nav>

      <div class="header-actions">
        <template v-if="authStore.isAuthenticated">
          <div class="user-info">
            <span class="username">{{ authStore.user?.username }}</span>
            <button class="btn-logout" @click="handleLogout">登出</button>
          </div>
        </template>
        <template v-else>
          <RouterLink to="/login" class="btn-ghost" style="font-size:0.85rem;padding:0.45rem 1rem;">
            登入
          </RouterLink>
        </template>
        
        <RouterLink v-if="authStore.hasPermission('skill:create')" to="/publish" class="btn-primary" style="font-size:0.85rem;padding:0.45rem 1rem;">
          ＋ 發布 Skill
        </RouterLink>
      </div>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<style scoped>
.header-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  font-size: 0.85rem;
}
.username {
  color: var(--text-primary);
  font-weight: 600;
}
.btn-logout {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-muted);
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-logout:hover {
  border-color: #ef4444;
  color: #ef4444;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(13, 17, 23, 0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-subtle);
}
.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 2rem;
}
.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}
.logo-icon { font-size: 1.3rem; }
.logo-text {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--text-primary);
}
.logo-badge {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 20px;
  background: var(--accent-dim);
  color: var(--accent);
  border: 1px solid rgba(37,164,100,0.3);
  letter-spacing: 0.03em;
  text-transform: uppercase;
}
.nav-links {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex: 1;
}
.nav-link {
  padding: 0.4rem 0.85rem;
  border-radius: 6px;
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
  transition: color 0.15s, background 0.15s;
}
.nav-link:hover, .nav-link.active {
  color: var(--text-primary);
  background: rgba(255,255,255,0.06);
}
</style>
