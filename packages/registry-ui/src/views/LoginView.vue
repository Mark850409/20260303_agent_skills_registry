<template>
  <div class="login-page fade-up">
    <div class="login-card card">
      <div class="login-header">
        <div class="logo-icon">🧠</div>
        <h2>管理員登入</h2>
        <p class="subtitle">進入 AI Skills & Apps 管理後台</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>使用者名稱</label>
          <input 
            v-model="form.username" 
            placeholder="輸入使用者名稱 (例如: admin)" 
            required
            :disabled="loading"
          />
        </div>
        <div class="form-group">
          <label>密碼</label>
          <input 
            v-model="form.password" 
            type="password" 
            placeholder="輸入密碼" 
            required
            :disabled="loading"
          />
        </div>
        
        <div v-if="error" class="error-msg">
          {{ error }}
        </div>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? '登入中...' : '立即登入' }}
        </button>
      </form>

      <div class="login-footer">
        <p>請輸入您的管理員帳號與密碼進行登入</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  password: ''
})

const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await authStore.login(form.username, form.password)
    
    // 如果是管理員，且沒有指定的 redirect，則導向管理後台
    let redirectPath = route.query.redirect
    if (!redirectPath) {
      redirectPath = authStore.isAdmin ? '/admin' : '/'
    }
    
    router.push(redirectPath)

  } catch (e) {
    error.value = '登入失敗，請檢查帳號資訊'
    console.error(e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: calc(100vh - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.login-card {
  width: 100%;
  max-width: 400px;
  padding: 2.5rem;
}
.login-header {
  text-align: center;
  margin-bottom: 2rem;
}
.login-header .icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 0.5rem;
}
.login-header h3 {
  margin-bottom: 0.3rem;
  font-size: 1.5rem;
}
.subtitle {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: #fff;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus {
  border-color: var(--accent);
}

.w-full {
  width: 100%;
  padding-top: 0.8rem;
  padding-bottom: 0.8rem;
  margin-top: 0.5rem;
}

.error-msg {
  color: #ef4444;
  font-size: 0.85rem;
  background: rgba(239, 68, 68, 0.1);
  padding: 0.6rem;
  border-radius: 6px;
  text-align: center;
}

.login-footer {
  margin-top: 2rem;
  text-align: center;
  font-size: 0.75rem;
  color: var(--text-muted);
}
.login-footer code {
  background: rgba(255,255,255,0.1);
  padding: 2px 4px;
  border-radius: 4px;
}
</style>
