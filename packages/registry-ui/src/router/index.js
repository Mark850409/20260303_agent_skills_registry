import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: () => import('@/views/HomeView.vue'),
        meta: { title: 'AgentSkills Registry' }
    },
    {
        path: '/skills',
        name: 'Browse',
        component: () => import('@/views/BrowseView.vue'),
        meta: { title: '瀏覽 Skills — AgentSkills Registry' }
    },
    {
        path: '/skills/:name',
        name: 'SkillDetail',
        component: () => import('@/views/SkillDetailView.vue'),
        meta: { title: 'Skill 詳情' }
    },
    {
        path: '/admin',
        name: 'Admin',
        component: () => import('@/views/AdminDashboard.vue'),
        meta: { title: '管理後台 — AgentSkills Registry', requiresAuth: true }
    },
    {
        path: '/publish',
        name: 'Publish',
        component: () => import('@/views/PublishView.vue'),
        meta: { title: '發布 Skill — AgentSkills Registry', requiresAuth: true }
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/LoginView.vue'),
        meta: { title: '登入 — AgentSkills Registry' }
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

    document.title = to.meta.title || 'AgentSkills Registry'

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        next({ name: 'Login', query: { redirect: to.fullPath } })
    } else {
        next()
    }
})

export default router
