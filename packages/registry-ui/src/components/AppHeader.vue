<template>
  <header class="app-header">
    <div class="header-inner">
      <RouterLink to="/" class="logo" @click="isMobileMenuOpen = false">
        <span class="logo-icon">🧠</span>
        <span class="logo-text">AI Skills & Apps</span>
        <span class="logo-badge">REGISTRY</span>
      </RouterLink>

      <button class="mobile-menu-btn" @click="isMobileMenuOpen = !isMobileMenuOpen" :aria-expanded="isMobileMenuOpen">
        <span class="hamburger-icon" :class="{ open: isMobileMenuOpen }"></span>
      </button>

      <nav class="nav-links" :class="{ 'mobile-open': isMobileMenuOpen }">
        <RouterLink to="/skills" class="nav-link" :class="{ active: $route.path.startsWith('/skills') }" @click="isMobileMenuOpen = false">
          🧩 Skills
        </RouterLink>
        <RouterLink to="/mcp" class="nav-link mcp-link" :class="{ active: $route.path.startsWith('/mcp') }" @click="isMobileMenuOpen = false">
          <span class="mcp-dot"></span>🔌 MCP
        </RouterLink>
        <RouterLink to="/docker" class="nav-link" :class="{ active: $route.path.startsWith('/docker') }" @click="isMobileMenuOpen = false">
          ⚓ Docker 倉庫
        </RouterLink>
        <RouterLink to="/npm" class="nav-link" :class="{ active: $route.path.startsWith('/npm') }" @click="isMobileMenuOpen = false">
          📦 NPM 倉庫
        </RouterLink>
        <RouterLink v-if="authStore.hasPermission('skill:create')" to="/publish" class="nav-link" :class="{ active: $route.path === '/publish' }" @click="isMobileMenuOpen = false">
          📤 發布
        </RouterLink>
        <RouterLink v-if="authStore.isAdmin" to="/admin" class="nav-link" :class="{ active: $route.path === '/admin' }" @click="isMobileMenuOpen = false">
          ⚙️ 管理
        </RouterLink>
        
        <!-- Mobile Actions -->
        <div class="mobile-only mobile-actions" v-if="isMobileMenuOpen">
          <template v-if="authStore.isAuthenticated">
            <div class="user-info-mobile">
              <span class="username">{{ authStore.user?.username }}</span>
              <button class="btn-logout" @click="handleLogout">登出</button>
            </div>
          </template>
          <template v-else>
            <RouterLink to="/login" class="btn-auth-mobile" @click="isMobileMenuOpen = false">登入</RouterLink>
          </template>
        </div>
      </nav>

      <div class="header-actions desktop-only">
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
        
        <div v-if="authStore.hasPermission('skill:create')" class="publish-dropdown" v-click-outside="closeDropdown">
          <button class="btn-primary publish-btn" @click="toggleDropdown">
            ＋ 發佈 <span class="dropdown-arrow" :class="{ open: dropdownOpen }">▾</span>
          </button>
          <div v-if="dropdownOpen" class="publish-menu">
            <RouterLink to="/publish?type=skill" class="publish-menu-item" @click="closeDropdown">
              <span class="menu-icon">🧩</span>
              <div class="menu-text">
                <strong>Agent Skill</strong>
                <span>AI 操作指令與腳本</span>
              </div>
            </RouterLink>
            <RouterLink to="/publish?type=mcp" class="publish-menu-item" @click="closeDropdown">
              <span class="menu-icon">🔌</span>
              <div class="menu-text">
                <strong>MCP Server</strong>
                <span>Model Context Protocol</span>
              </div>
            </RouterLink>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

const dropdownOpen = ref(false)
const isMobileMenuOpen = ref(false)

function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value
}

function closeDropdown() {
  dropdownOpen.value = false
}

function handleLogout() {
  authStore.logout()
  isMobileMenuOpen.value = false
  router.push('/')
}

// Click outside directive
const vClickOutside = {
  mounted(el, binding) {
    el._clickOutsideHandler = (e) => {
      if (!el.contains(e.target)) binding.value()
    }
    document.addEventListener('click', el._clickOutsideHandler)
  },
  unmounted(el) {
    document.removeEventListener('click', el._clickOutsideHandler)
  }
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

/* 發佈下拉選單 */
.publish-dropdown {
  position: relative;
}
.publish-btn {
  font-size: 0.85rem;
  padding: 0.45rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.dropdown-arrow {
  font-size: 0.7rem;
  transition: transform 0.2s;
  display: inline-block;
}
.dropdown-arrow.open {
  transform: rotate(180deg);
}
.publish-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 210px;
  background: var(--bg-secondary, #161b22);
  border: 1px solid var(--border, rgba(255,255,255,0.1));
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  overflow: hidden;
  z-index: 999;
  animation: menuFadeIn 0.15s ease;
}
@keyframes menuFadeIn {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.publish-menu-item {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.85rem 1rem;
  color: var(--text-secondary);
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.publish-menu-item:last-child { border-bottom: none; }
.publish-menu-item:hover {
  background: rgba(255,255,255,0.05);
  color: var(--text-primary);
}
.menu-icon { font-size: 1.4rem; flex-shrink: 0; }
.menu-text { display: flex; flex-direction: column; }
.menu-text strong { font-size: 0.88rem; color: var(--text-primary); font-weight: 600; }
.menu-text span { font-size: 0.74rem; color: var(--text-muted); margin-top: 1px; }
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
  height: 64px;
  display: flex;
  align-items: center;
  gap: 2rem;
  position: relative;
}
.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
  z-index: 102;
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
  padding: 0.5rem 0.9rem;
  border-radius: 8px;
  font-size: 0.92rem;
  color: var(--text-secondary);
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.nav-link:hover, .nav-link.active {
  color: var(--text-primary);
  background: rgba(255,255,255,0.08);
}
.mcp-link .mcp-dot { width: 6px; height: 6px; border-radius: 50%; background: #f97316; opacity: 0.7; }
.mcp-link:hover, .mcp-link.active { color: #f97316; background: rgba(249,115,22,0.1); }
.mcp-link.active .mcp-dot { opacity: 1; }

/* Mobile Menu Button */
.mobile-menu-btn {
  display: none;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 10px;
  z-index: 102;
}

.hamburger-icon {
  display: block;
  width: 22px;
  height: 2px;
  background: var(--text-primary);
  position: relative;
  transition: all 0.3s;
}

.hamburger-icon::before,
.hamburger-icon::after {
  content: '';
  position: absolute;
  width: 22px;
  height: 2px;
  background: var(--text-primary);
  transition: all 0.3s;
}

.hamburger-icon::before { top: -6px; }
.hamburger-icon::after { bottom: -6px; }

.hamburger-icon.open { background: transparent; }
.hamburger-icon.open::before { transform: rotate(45deg); top: 0; }
.hamburger-icon.open::after { transform: rotate(-45deg); bottom: 0; }

.mobile-only { display: none; }

@media (max-width: 992px) {
  .header-inner { gap: 1rem; }
  .logo-text { font-size: 1rem; }
  .logo-badge { display: none; }
}

@media (max-width: 768px) {
  .mobile-menu-btn { display: block; }
  .desktop-only { display: none !important; }
  .mobile-only { display: block; }
  
  .nav-links {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100vh;
    background: #0d1117;
    flex-direction: column;
    padding: 80px 1.5rem 2rem;
    gap: 0.5rem;
    transform: translateX(100%);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 101;
    overflow-y: auto;
  }
  
  .nav-links.mobile-open {
    transform: translateX(0);
  }
  
  .nav-link {
    width: 100%;
    padding: 1rem;
    font-size: 1.1rem;
    border-radius: 12px;
    background: rgba(255,255,255,0.03);
  }
  
  .mobile-actions {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid var(--border-subtle);
    width: 100%;
  }
  
  .user-info-mobile {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .user-info-mobile .username {
    font-size: 1.2rem;
    color: var(--text-primary);
  }
  
  .user-info-mobile .btn-logout {
    padding: 0.8rem;
    font-size: 1rem;
    width: 100%;
  }
  
  .btn-auth-mobile {
    display: block;
    width: 100%;
    padding: 1rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    text-align: center;
    color: var(--text-primary);
    text-decoration: none;
    font-weight: 600;
  }
}
</style>
