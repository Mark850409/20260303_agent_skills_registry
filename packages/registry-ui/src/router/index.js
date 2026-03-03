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
        path: '/publish',
        name: 'Publish',
        component: () => import('@/views/PublishView.vue'),
        meta: { title: '發布 Skill — AgentSkills Registry' }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior() {
        return { top: 0 }
    }
})

router.afterEach(to => {
    document.title = to.meta.title || 'AgentSkills Registry'
})

export default router
