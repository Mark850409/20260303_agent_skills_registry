<template>
  <div class="kb-page">
    <header class="kb-header">
      <h1 class="kb-title">💡 提示詞知識庫</h1>
      <p class="kb-subtitle">在這裡探索由社群成員建立並分享的高品質 AI 提示詞 (Prompt)，幫助您快速達成目標。</p>
    </header>

    <div class="kb-container">
      <!-- Search and Filter Bar -->
      <div class="kb-toolbar card">
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchQuery" 
            @keyup.enter="fetchKnowledgeBase"
            placeholder="搜尋標題、內容或關鍵字..." 
            class="pg-input"
          />
          <button class="search-btn" @click="fetchKnowledgeBase">🔍</button>
        </div>
        
        <div class="filter-box">
          <input 
            type="text" 
            v-model="tagQuery" 
            @keyup.enter="fetchKnowledgeBase"
            placeholder="標籤過濾 (e.g., Python)" 
            class="pg-input"
          />
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>載入知識庫中...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="prompts.length === 0" class="empty-state card">
        <span class="empty-icon">📭</span>
        <h3>找不到相符的提示詞</h3>
        <p>請嘗試使用其他關鍵字或標籤進行搜尋。</p>
      </div>

      <!-- Prompt Cards Grid -->
      <div v-else class="kb-grid">
        <div v-for="prompt in prompts" :key="prompt.id" class="kb-card card">
          <div class="kb-card-header">
            <h3 class="kb-card-title">{{ prompt.title }}</h3>
            <button @click="copyPrompt(prompt)" class="copy-btn" :title="'複製提示詞'">
              {{ copiedId === prompt.id ? '✔ 已複製' : '📋 複製' }}
            </button>
          </div>
          
          <p class="kb-card-desc" v-if="prompt.description">{{ prompt.description }}</p>
          
          <div class="kb-tags" v-if="prompt.tags && prompt.tags.length > 0">
            <span v-for="tag in prompt.tags" :key="tag" class="kb-tag" @click="filterByTag(tag)">
              #{{ tag }}
            </span>
          </div>
          
          <div class="kb-preview">
            <pre><code>{{ truncate(prompt.prompt_content, 150) }}</code></pre>
          </div>
          
          <div class="kb-card-footer">
            <span class="kb-date">{{ formatDate(prompt.created_at) }}</span>
            <button @click="viewFullPrompt(prompt)" class="btn-ghost-small">查看完整內容</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Full Prompt View Modal -->
    <div v-if="selectedPrompt" class="kb-modal-overlay" @click.self="selectedPrompt = null">
      <div class="kb-modal-content large-modal">
        <div class="modal-header">
          <h2 class="modal-title">{{ selectedPrompt.title }}</h2>
          <button class="close-btn" @click="selectedPrompt = null">✕</button>
        </div>
        
        <div class="modal-body">
          <p class="modal-desc" v-if="selectedPrompt.description">{{ selectedPrompt.description }}</p>
          <div class="modal-tags" v-if="selectedPrompt.tags && selectedPrompt.tags.length > 0">
            <span v-for="tag in selectedPrompt.tags" :key="tag" class="kb-tag">#{{ tag }}</span>
          </div>
          
          <div class="modal-prompt-area">
            <textarea 
              class="full-prompt-textarea" 
              :value="selectedPrompt.prompt_content"
              readonly
            ></textarea>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="copyPrompt(selectedPrompt)" class="btn-primary">
            {{ copiedId === selectedPrompt.id ? '✔ 已成功複製！' : '📋 複製完整提示詞' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const prompts = ref([])
const isLoading = ref(true)
const searchQuery = ref('')
const tagQuery = ref('')
const copiedId = ref(null)
const selectedPrompt = ref(null)

const fetchKnowledgeBase = async () => {
  isLoading.value = true
  try {
    const params = new URLSearchParams()
    if (searchQuery.value) params.append('search', searchQuery.value)
    if (tagQuery.value) params.append('tag', tagQuery.value)
      
    const res = await fetch(`/api/prompts/knowledge/public?${params.toString()}`)
    if (res.ok) {
      prompts.value = await res.json()
    } else {
      console.error('Failed to fetch knowledge base')
    }
  } catch (err) {
    console.error('Error fetching knowledge base:', err)
  } finally {
    isLoading.value = false
  }
}

const copyPrompt = async (prompt) => {
  try {
    await navigator.clipboard.writeText(prompt.prompt_content)
    copiedId.value = prompt.id
    setTimeout(() => { copiedId.value = null }, 2000)
  } catch (err) {
    alert('複製失敗，請手動選取文字複製。')
  }
}

const viewFullPrompt = (prompt) => {
  selectedPrompt.value = prompt
}

const filterByTag = (tag) => {
  tagQuery.value = tag
  searchQuery.value = ''
  fetchKnowledgeBase()
}

const truncate = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('zh-TW', {
    year: 'numeric', month: 'short', day: 'numeric'
  }).format(date)
}

onMounted(() => {
  fetchKnowledgeBase()
})
</script>

<style scoped>
.kb-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}
.kb-header {
  text-align: center;
  margin-bottom: 2.5rem;
}
.kb-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 2.2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 0.5rem 0;
}
.kb-subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
}

/* Toolbar */
.kb-toolbar {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  background: var(--bg-card);
  align-items: center;
}
.search-box, .filter-box {
  display: flex;
  position: relative;
  flex: 1;
}
.filter-box {
  flex: 0.5;
}
.pg-input {
  width: 100%;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 0.85rem 1rem;
  color: var(--text-primary);
  font-size: 0.95rem;
  transition: all 0.2s;
}
.pg-input:focus {
  border-color: var(--accent);
  outline: none;
  box-shadow: 0 0 0 3px rgba(37, 164, 100, 0.1);
}
.search-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  font-size: 1.1rem;
}

/* Grid & Cards */
.kb-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}
.kb-card {
  display: flex;
  flex-direction: column;
  padding: 1.5rem;
  transition: transform 0.2s, box-shadow 0.2s;
}
.kb-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.4);
  border-color: var(--border-hover);
}
.kb-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 0.75rem;
}
.kb-card-title {
  font-size: 1.25rem;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.4;
}
.copy-btn {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.copy-btn:hover {
  background: var(--accent-dim);
  color: var(--accent);
  border-color: var(--accent);
}
.kb-card-desc {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.6;
  margin: 0 0 1rem 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.kb-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}
.kb-tag {
  background: rgba(168, 85, 247, 0.1);
  color: #c084fc;
  border: 1px solid rgba(168, 85, 247, 0.2);
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}
.kb-tag:hover {
  background: rgba(168, 85, 247, 0.2);
}
.kb-preview {
  background: rgba(0,0,0,0.2);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  flex: 1;
}
.kb-preview pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: 'Fira Code', monospace;
  font-size: 0.85rem;
  color: var(--text-muted);
}
.kb-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-subtle);
  padding-top: 1rem;
  margin-top: auto;
}
.kb-date {
  font-size: 0.8rem;
  color: var(--text-muted);
}
.btn-ghost-small {
  background: transparent;
  border: none;
  color: #38bdf8;
  font-size: 0.85rem;
  cursor: pointer;
}
.btn-ghost-small:hover {
  text-decoration: underline;
}

/* Modal */
.kb-modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100vw; height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.kb-modal-content {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0,0,0,0.5);
  animation: modalPop 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-title { margin: 0; font-size: 1.4rem; color: var(--text-primary); }
.close-btn { background: transparent; border: none; color: var(--text-muted); font-size: 1.2rem; cursor: pointer; }
.close-btn:hover { color: var(--text-primary); }
.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.modal-desc {
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 1rem 0;
}
.modal-tags {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}
.full-prompt-textarea {
  width: 100%;
  flex: 1;
  min-height: 300px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 1.25rem;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.95rem;
  line-height: 1.6;
  resize: none;
  outline: none;
}
.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--border-subtle);
  display: flex;
  justify-content: flex-end;
}
.btn-primary {
  background: var(--accent);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-primary:hover {
  background: var(--accent-hover);
}

/* Loading & Empty States */
.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: var(--text-muted);
}
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255,255,255,0.1);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}
@keyframes spin { 100% { transform: rotate(360deg); } }
.empty-icon { font-size: 3rem; margin-bottom: 1rem; opacity: 0.5; }

@media (max-width: 768px) {
  .kb-toolbar { flex-direction: column; }
  .filter-box { width: 100%; }
}
</style>
