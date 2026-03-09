import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: () => import('@/views/HomeView.vue'),
        meta: { title: 'AI Skills & Apps Registry' }
    },
    {
        path: '/skills',
        name: 'Browse',
        component: () => import('@/views/BrowseView.vue'),
        meta: { title: '瀏覽 Skills — AI Skills & Apps Registry' }
    },
    {
        path: '/prompt-generator',
        name: 'PromptGenerator',
        component: () => import('@/views/PromptGeneratorView.vue'),
        meta: { title: '提示詞助理 — AI Skills & Apps Registry' }
    },
    {
        path: '/skills/:name',
        name: 'SkillDetail',
        component: () => import('@/views/SkillDetailView.vue'),
        meta: { title: 'Skill 詳情' }
    },
    {
        path: '/mcp',
        name: 'McpBrowse',
        component: () => import('@/views/McpBrowseView.vue'),
        meta: { title: 'MCP Servers — AI Skills & Apps Registry' }
    },
    {
        path: '/mcp/:name',
        name: 'McpDetail',
        component: () => import('@/views/McpDetailView.vue'),
        meta: { title: 'MCP Server 詳情' }
    },
    {
        path: '/admin',
        name: 'Admin',
        component: () => import('@/views/AdminDashboard.vue'),
        meta: { title: '管理後台 — AI Skills & Apps Registry', requiresAuth: true }
    },
    {
        path: '/publish',
        name: 'Publish',
        component: () => import('@/views/PublishView.vue'),
        meta: { title: '發布 Skill — AI Skills & Apps Registry', requiresAuth: true }
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/LoginView.vue'),
        meta: { title: '登入 — AI Skills & Apps Registry' }
    },
    {
        path: '/docker',
        name: 'DockerRegistry',
        component: () => import('@/views/DockerRegistryView.vue'),
        meta: { title: 'Docker 倉庫 — AI Skills & Apps Registry' }
    },
    {
        path: '/docker/:repo+',
        name: 'DockerRepoDetail',
        component: () => import('@/views/DockerRepoDetailView.vue'),
        meta: { title: '倉庫詳情 — AI Skills & Apps Registry' }
    },
    {
        path: '/npm',
        name: 'NpmRegistry',
        component: () => import('@/views/NpmRegistryView.vue'),
        meta: { title: 'NPM 倉庫 — AI Skills & Apps Registry' }
    },
    {
        path: '/npm/:name+',
        name: 'NpmPackageDetail',
        component: () => import('@/views/NpmPackageDetailView.vue'),
        meta: { title: 'NPM 套件詳情 — AI Skills & Apps Registry' }
    },
    {
        path: '/prompts/knowledge',
        name: 'PromptKnowledge',
        component: () => import('@/views/PromptKnowledgeView.vue'),
        meta: { title: '提示詞知識庫 — AI Skills & Apps Registry' }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior() {
        return { top: 0 }
    }
})

import { useAuthStore } from '@/store/auth'

router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()

    // Auto-login if token exists
    if (!authStore.user && authStore.token) {
        try {
            await authStore.fetchMe()
        } catch (e) {
            console.error('Auto-login failed', e)
        }
    }

    document.title = to.meta.title || 'AI Skills & Apps Registry'

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        next({ name: 'Login', query: { redirect: to.fullPath } })
    } else {
        next()
    }
})

export default router
