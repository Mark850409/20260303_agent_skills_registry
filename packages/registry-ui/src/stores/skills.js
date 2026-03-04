import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { skillsApi } from '@/api'

export const useSkillsStore = defineStore('skills', () => {
    const skills = ref([])
    const allSkills = ref([])   // 所有 skill，用於分類計數
    const total = ref(0)
    const page = ref(1)
    const pages = ref(1)
    const loading = ref(false)
    const tags = ref([])
    const stats = ref({ total_skills: 0, total_downloads: 0 })
    const currentSkill = ref(null)

    const perPage = 20

    async function fetchSkills(params = {}) {
        loading.value = true
        try {
            const res = await skillsApi.list({ page: page.value, per_page: perPage, ...params })
            skills.value = res.data.skills
            total.value = res.data.total
            pages.value = res.data.pages
        } finally {
            loading.value = false
        }
    }

    async function fetchSkill(name) {
        loading.value = true
        currentSkill.value = null
        try {
            const res = await skillsApi.get(name)
            currentSkill.value = res.data
        } finally {
            loading.value = false
        }
    }

    async function fetchTags() {
        const res = await skillsApi.tags()
        tags.value = res.data
    }

    async function fetchStats() {
        const res = await skillsApi.stats()
        stats.value = res.data
    }

    /** 一次擈取大量 skills（不影響現有分頁），用於分類計數 */
    async function fetchAllForCount() {
        try {
            const res = await skillsApi.list({ page: 1, per_page: 500, sort: 'downloads' })
            allSkills.value = res.data.skills || []
        } catch (e) {
            console.warn('fetchAllForCount failed', e)
        }
    }

    return {
        skills, allSkills, total, page, pages, loading, tags, stats, currentSkill, perPage,
        fetchSkills, fetchSkill, fetchTags, fetchStats, fetchAllForCount
    }
})
