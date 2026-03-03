import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
    const token = ref(localStorage.getItem('token') || '')
    const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

    const isAuthenticated = computed(() => !!token.value)
    const isAdmin = computed(() => user.value?.role === 'admin')
    const permissions = computed(() => user.value?.permissions || [])

    function hasPermission(perm) {
        if (isAdmin.value) return true
        return permissions.value.includes(perm)
    }

    async function login(username, email) {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email })
        })
        if (!res.ok) throw new Error('Login failed')

        const data = await res.json()
        token.value = data.api_token

        // Fetch user details manually or from login response
        // For now, let's assume we need to call /api/auth/me to get the role/perms
        await fetchMe(data.api_token)
    }

    async function fetchMe(useToken = token.value) {
        if (!useToken) return
        const res = await fetch('/api/auth/me', {
            headers: { 'Authorization': `Bearer ${useToken}` }
        })
        if (res.ok) {
            const data = await res.json()
            user.value = data
            localStorage.setItem('token', useToken)
            localStorage.setItem('user', JSON.stringify(data))
        } else {
            logout()
        }
    }

    function logout() {
        token.value = ''
        user.value = null
        localStorage.removeItem('token')
        localStorage.removeItem('user')
    }

    return {
        token,
        user,
        isAuthenticated,
        isAdmin,
        permissions,
        hasPermission,
        login,
        logout,
        fetchMe
    }
})
