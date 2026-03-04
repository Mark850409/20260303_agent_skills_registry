import axios from 'axios'

const api = axios.create({
    baseURL: '/api',
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' }
})

// Attach API token if stored
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token')
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
})

export const skillsApi = {
    /**
     * 搜尋 / 列出 skills
     * @param {Object} params - { q, tags, sort, page, per_page }
     */
    list(params = {}) {
        return api.get('/skills', { params })
    },

    /** 取得 Skill 詳情 */
    get(name) {
        return api.get(`/skills/${name}`)
    },

    /** 取得特定版本 */
    getVersion(name, version) {
        return api.get(`/skills/${name}/${version}`)
    },

    /** 取得所有標籤 */
    tags() {
        return api.get('/skills/tags')
    },

    /** 全站統計 */
    stats() {
        return api.get('/skills/stats')
    },

    /** 以 JSON 方式 push skill */
    push(payload) {
        return api.post('/skills', payload)
    },

    /** 取得下載 URL */
    downloadUrl(name, version = null) {
        return version ? `/api/skills/${name}/${version}/download` : `/api/skills/${name}/download`
    }
}

export const authApi = {
    login(username, email) {
        return api.post('/auth/login', { username, email })
    },
    me() {
        return api.get('/auth/me')
    }
}

export default api
