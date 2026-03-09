<template>
  <div class="generator-page">
    <header class="generator-header">
      <h1 class="generator-title">✨ 進階提示詞助理</h1>
      <p class="generator-subtitle">只要輸入簡短需求，由 AI 幫您自動擴寫成結構完整的高品質專業 Prompt。</p>
    </header>

    <div class="generator-layout">
      <!-- Left Column: Controls -->
      <div class="generator-sidebar">
        
        <!-- Step 1: Scenario & Task -->
        <div class="card pg-card">
          <h2 class="pg-card-title">
            <span class="step-badge">1</span>
            基礎任務設定
          </h2>
          
          <div class="pg-form-group">
            <label class="pg-label">任務類型 (Scenario)</label>
            <div class="scenario-grid">
              <button v-for="scen in scenarios" :key="scen.id" 
                      @click="form.scenario = scen.id"
                      class="scenario-btn"
                      :class="{ active: form.scenario === scen.id }">
                {{ scen.name }}
              </button>
            </div>
          </div>

          <div class="pg-form-group">
            <label class="pg-label">主要任務 (Task) <span class="required">*</span></label>
            <p class="pg-hint">請簡短描述你想讓 AI 做什麼？ (例如：寫一個 Python 爬蟲程式)</p>
            <textarea v-model="form.task" rows="3" placeholder="請輸入核心任務..." class="pg-input"></textarea>
          </div>

          <div class="pg-form-group">
            <label class="pg-label">補充背景資訊 (Context)</label>
            <p class="pg-hint">提供一些前提條件或背景資料，讓 AI 更了解狀況。</p>
            <textarea v-model="form.context" rows="2" placeholder="例如：這是要用在我們公司內部工具的、受眾是國小學生..." class="pg-input"></textarea>
          </div>
        </div>

        <!-- Step 2: Advanced Options -->
        <div class="card pg-card">
          <div class="pg-card-header-flex">
            <h2 class="pg-card-title no-margin">
              <span class="step-badge alt">2</span>
              進階參數選項
            </h2>
            <button @click="showAdvanced = !showAdvanced" class="pg-toggle-btn">
              {{ showAdvanced ? '收起選項 ▾' : '展開選項 ▴' }}
            </button>
          </div>

          <div v-show="showAdvanced" class="pg-advanced-options fade-in">
            <!-- Role -->
            <div class="pg-form-group">
              <label class="pg-label">AI 扮演角色 (Role)</label>
              <select v-model="form.role" class="pg-select">
                <optgroup v-for="(roles, category) in roleGroups" :key="category" :label="category">
                  <option v-for="role in roles" :key="role" :value="role">{{ role }}</option>
                </optgroup>
              </select>
            </div>

            <!-- Output Format -->
            <div class="pg-form-group">
              <label class="pg-label">AI 最終回覆格式 (Output Format)</label>
              <p class="pg-hint">你想讓套用此提示詞的 AI 用什麼格式回答你？(例如：產生出來的爬蟲結果要用 JSON 呈現)</p>
              <div class="pg-pill-group">
                <button v-for="fmt in formats" :key="fmt"
                        @click="form.format = fmt"
                        class="pg-pill"
                        :class="{ active: form.format === fmt }">
                  {{ fmt }}
                </button>
              </div>
            </div>

            <!-- Tone -->
            <div class="pg-form-group">
              <label class="pg-label">語氣與風格 (Tone)</label>
              <div class="pg-pill-group">
                <button v-for="t in availableTones" :key="t"
                        @click="form.tone = t"
                        class="pg-pill small"
                        :class="{ active: form.tone === t }">
                  {{ t }}
                </button>
              </div>
            </div>

            <!-- Constraints -->
            <div class="pg-form-group">
              <label class="pg-label">限制與要求 (Constraints)</label>
              <div class="pg-checkbox-group">
                <label v-for="req in availableConstraints" :key="req" class="pg-checkbox-label">
                  <input type="checkbox" :value="req" v-model="form.constraints" class="pg-checkbox">
                  <span>{{ req }}</span>
                </label>
              </div>
            </div>
          </div>
          
          <div v-show="!showAdvanced" class="pg-advanced-hidden">
            <p>已隱藏進階選項 (套用預設值)</p>
          </div>
        </div>
      </div>

      <!-- Right Column: Result Preview -->
      <div class="generator-main">
        <!-- Empty State / Generate Button -->
        <div class="card pg-preview-card empty-state" v-if="!optimizedResult && !isOptimizing">
           <div class="empty-icon-wrapper">
             <span class="empty-icon">✨</span>
           </div>
           <h3 class="empty-title">準備好生成你的專業提示詞了嗎？</h3>
           <p class="empty-desc">填寫左側的任務需求，然後點擊下方按鈕，讓 AI 自動為你擴寫成完美的指令。</p>
           
           <div class="generate-actions">
             <label class="pg-label">選擇優化模型:</label>
             <select v-model="provider" class="pg-select mb-md">
               <option value="openai">🎯 OpenAI (GPT-4o)</option>
               <option value="google">⚡ Google (Gemini 2.5 Flash)</option>
             </select>

             <button @click="optimizePrompt" :disabled="!form.task || isOptimizing" class="pg-generate-btn">
               ✨ 讓 AI 幫我神準擴寫
             </button>
           </div>
        </div>

        <!-- Loading / Result State -->
        <div v-else class="card pg-preview-card result-state">
          <!-- Header -->
          <div class="result-header">
            <h2 class="result-title">🚀 優化完成的 Prompt</h2>
            <button @click="resetFlow" class="pg-reset-btn">重新產生</button>
          </div>
          
          <!-- Loading State -->
          <div v-if="isOptimizing" class="loading-state">
            <div class="spinner"></div>
            <h3 class="loading-title">正在透過 {{ provider === 'openai' ? 'GPT-4o' : 'Gemini' }} 優化指令...</h3>
            <p class="loading-desc">這可能需要大約 5-10 秒鐘，AI 正在建構角色與制定標準流程。</p>
          </div>

          <!-- Result State -->
          <div v-else-if="optimizedResult" class="result-content-wrapper">
            <!-- Render Single Text Block -->
            <div class="result-scroll-area flex-col-area">
              <button @click="copyRawJson" class="copy-json-btn" title="複製原始 JSON">📋</button>
              
              <textarea 
                class="full-prompt-textarea" 
                :value="formattedPromptText"
                readonly
              ></textarea>
            </div>

            <!-- Actions Bottom Bar -->
            <div class="result-footer" style="display:flex; align-items:center; gap: 1rem;">
              <button @click="copyFormattedText" class="pg-copy-main-btn" style="flex:1;">
                {{ copyStatus }}
              </button>
              <button @click="openKbModal" class="pg-save-kb-btn">
                💾 存入知識庫
              </button>
            </div>
            <p class="result-footer-hint" style="margin-top: 0.5rem;">複製為純文字格式，直接貼上給 LLM 即可開始對話。</p>
          </div>
        </div>
      </div>

    </div>

    <!-- Modal for Saving to KB -->
    <div v-if="showKbModal" class="kb-modal-overlay" @click.self="closeKbModal">
      <div class="kb-modal-content">
        <h3 class="kb-modal-title">💾 儲存至提示詞知識庫</h3>
        
        <div class="pg-form-group">
          <label class="pg-label">標題 (Title) <span class="required">*</span></label>
          <input type="text" v-model="kbForm.title" class="pg-input" placeholder="幫這個提示詞取個好懂的名字...">
        </div>
        
        <div class="pg-form-group">
          <label class="pg-label">簡介 (Description)</label>
          <textarea v-model="kbForm.description" class="pg-input" rows="2" placeholder="簡短說明這個提示詞的使用情境或效果..."></textarea>
        </div>
        
        <div class="pg-form-group">
          <label class="pg-label">標籤 (Tags)</label>
          <p class="pg-hint">請用半形逗號分開多個標籤 (例如: Python,爬蟲,新手)</p>
          <input type="text" v-model="kbForm.tagsInput" class="pg-input" placeholder="Python, WebScraping...">
        </div>
        
        <div class="kb-modal-actions">
          <button class="btn-cancel" @click="closeKbModal">取消</button>
          <button class="btn-save" @click="saveToKb" :disabled="isSavingKb || !kbForm.title.trim()">
            {{ isSavingKb ? '儲存中...' : '確認儲存' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

const provider = ref('openai')
const isOptimizing = ref(false)
const showAdvanced = ref(true)
const optimizedResult = ref(null)
const copyStatus = ref('📋 複製完整提示詞 (文字版)')

const showKbModal = ref(false)
const isSavingKb = ref(false)
const kbForm = reactive({
  title: '',
  description: '',
  tagsInput: ''
})

const formattedPromptText = computed(() => {
  if (!optimizedResult.value) return ''
  const res = optimizedResult.value
  let text = `# Role: ${res.Role || ''}\n\n`
  if (res.Description) text += `## Description\n${res.Description}\n\n`
  if (res.Definition) text += `## Definition\n${res.Definition}\n\n`
  if (res.Goals) text += `## Goals\n${res.Goals}\n\n`
  if (res.Skills) text += `## Skills\n${res.Skills}\n\n`
  if (res.Workflows) text += `## Workflows\n${res.Workflows}\n\n`
  if (res.Constraints) text += `## Constraints\n${res.Constraints}\n\n`
  if (res.OutputFormat) text += `## Output Format\n${res.OutputFormat}\n\n`
  if (res.Initialization) text += `## Initialization\n${res.Initialization}`
  return text.trim()
})

const scenarios = ref([])
const roleGroups = ref({})
const formats = ref([])
const availableTones = ref([])
const availableConstraints = ref([])

const form = reactive({
  scenario: 'general',
  task: '',
  context: '',
  role: '無指定 (由 AI 推斷最佳角色)',
  format: 'Markdown 文章',
  tone: '',
  constraints: []
})

onMounted(async () => {
  try {
    const res = await fetch('/api/prompt-settings/public')
    if (res.ok) {
      const data = await res.json()
      scenarios.value = data.scenarios || []
      formats.value = data.formats || []
      availableTones.value = data.tones || []
      availableConstraints.value = data.constraints || []
      roleGroups.value = data.roleGroups || {}
      
      // Update form defaults based on fetched data
      if (scenarios.value.length > 0) form.scenario = scenarios.value[0].id;
      if (formats.value.length > 0) form.format = formats.value[0];
      
      // Ensure "No specific role" is always an option at the top
      let hasDefault = false
      for (const roles of Object.values(roleGroups.value)) {
        if (roles.includes('無指定 (由 AI 推斷最佳角色)')) {
          hasDefault = true
          break
        }
      }
      if (!hasDefault) {
         if (!roleGroups.value['General']) roleGroups.value['General'] = []
         roleGroups.value['General'].unshift('無指定 (由 AI 推斷最佳角色)')
      }
      form.role = '無指定 (由 AI 推斷最佳角色)'
    }
  } catch (err) {
    console.error('Failed to fetch prompt settings:', err)
  }
})

const toggleSelection = (array, item) => {
  const index = array.indexOf(item)
  if (index > -1) array.splice(index, 1)
  else array.push(item)
}

const optimizePrompt = async () => {
  if (!form.task.trim()) return
  
  isOptimizing.value = true
  optimizedResult.value = null
  
  try {
    const response = await fetch('/api/prompts/optimize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        provider: provider.value,
        scenario: form.scenario,
        data: {
          task: form.task,
          context: form.context,
          role: form.role,
          format: form.format,
          tones: form.tone ? [form.tone] : [],
          constraints: form.constraints
        }
      })
    })
    
    if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
    }
    
    const data = await response.json()
    optimizedResult.value = data
    
  } catch (error) {
    console.error('Failed to optimize prompt:', error)
    alert('優化提示詞時發生錯誤，請檢查網路連線或系統日誌。')
  } finally {
    isOptimizing.value = false
  }
}

const resetFlow = () => {
    optimizedResult.value = null
}

const copyRawJson = async () => {
    if (!optimizedResult.value) return
    try {
        await navigator.clipboard.writeText(JSON.stringify(optimizedResult.value, null, 2))
        alert('JSON 格式已複製到剪貼簿！')
    } catch {
        // ignore
    }
}

const copyFormattedText = async () => {
  if (!optimizedResult.value) return
  
  const res = optimizedResult.value
  let text = `# Role: ${res.Role || ''}\n\n`
  text += `## Description\n${res.Description || ''}\n\n`
  text += `## Definition\n${res.Definition || ''}\n\n`
  text += `## Goals\n${res.Goals || ''}\n\n`
  text += `## Skills\n${res.Skills || ''}\n\n`
  text += `## Workflows\n${res.Workflows || ''}\n\n`
  text += `## Constraints\n${res.Constraints || ''}\n\n`
  text += `## Output Format\n${res.OutputFormat || ''}\n\n`
  text += `## Initialization\n${res.Initialization || ''}`
  
  try {
    await navigator.clipboard.writeText(text)
    copyStatus.value = '✔ 已成功複製！'
    setTimeout(() => { copyStatus.value = '📋 複製完整提示詞 (文字版)' }, 2500)
  } catch (err) {
    alert('複製失敗，請手動選取文字複製。')
  }
}

const openKbModal = () => {
  kbForm.title = form.task.slice(0, 30) // Set initial title based on task
  kbForm.description = form.context
  kbForm.tagsInput = ''
  showKbModal.value = true
}

const closeKbModal = () => {
  showKbModal.value = false
}

const saveToKb = async () => {
  if (!kbForm.title.trim()) return
  
  isSavingKb.value = true
  try {
    const payload = {
      title: kbForm.title.trim(),
      description: kbForm.description.trim(),
      prompt_content: formattedPromptText.value,
      tags: kbForm.tagsInput.split(',').map(t => t.trim()).filter(Boolean),
      is_public: true
    }
    
    const res = await fetch('/api/prompts/knowledge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    
    if (res.ok) {
        alert('🎉 成功存入提示詞知識庫！')
        closeKbModal()
    } else {
        alert('儲存失敗，請稍後再試。')
    }
  } catch (err) {
    console.error('Failed to save to KB:', err)
    alert('儲存發生錯誤：' + err.message)
  } finally {
    isSavingKb.value = false
  }
}
</script>

<style scoped>
.generator-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}
.generator-header {
  text-align: center;
  margin-bottom: 2.5rem;
}
.generator-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 2.2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #48c082 0%, #38bdf8 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 0.5rem 0;
}
.generator-subtitle {
  color: var(--text-secondary);
  font-size: 1rem;
}

/* Layout */
.generator-layout {
  display: flex;
  gap: 2rem;
  align-items: flex-start;
}
.generator-sidebar {
  flex: 1.4;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.generator-main {
  flex: 1;
  position: sticky;
  top: 80px;
}

/* Cards */
.pg-card {
  padding: 1.5rem;
}
.pg-card-title {
  display: flex;
  align-items: center;
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0 0 1.2rem 0;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-primary);
}
.pg-card-title.no-margin {
  border-bottom: none;
  padding-bottom: 0;
  margin: 0;
}
.pg-card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.2rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border-subtle);
}
.step-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--accent-dim);
  color: var(--accent);
  margin-right: 0.8rem;
  font-size: 0.9rem;
}
.step-badge.alt {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
}

/* Forms */
.pg-form-group {
  margin-bottom: 1.2rem;
}
.pg-form-group:last-child {
  margin-bottom: 0;
}
.pg-label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}
.required {
  color: #ef4444;
}
.pg-hint {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: -0.3rem;
  margin-bottom: 0.5rem;
}
.pg-input {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-primary);
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.9rem;
  resize: vertical;
  transition: all 0.2s;
}
.pg-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 1px var(--accent-dim);
}
.pg-select {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-primary);
  border-radius: 8px;
  font-size: 0.9rem;
  outline: none;
  cursor: pointer;
  appearance: auto;
}
.pg-select:focus {
  border-color: var(--accent);
}
.pg-select optgroup {
  background: var(--bg-primary);
  color: var(--text-muted);
}
.pg-select option {
  background: var(--bg-secondary);
  color: var(--text-primary);
}
.mb-md { margin-bottom: 1.5rem; }

/* Grid Buttons */
.scenario-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.5rem;
}
.scenario-btn {
  padding: 0.75rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}
.scenario-btn:hover {
  border-color: var(--text-muted);
}
.scenario-btn.active {
  background: var(--accent-dim);
  border-color: var(--accent);
  color: var(--accent);
}

/* Pills */
.pg-pill-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.pg-pill {
  padding: 0.5rem 1rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}
.pg-pill:hover {
  border-color: var(--text-muted);
}
.pg-pill.active {
  background: rgba(168, 85, 247, 0.15);
  border-color: #a855f7;
  color: #e9d5ff;
}
.pg-pill.small {
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
}
.pg-pill.small.active {
  background: rgba(56, 189, 248, 0.15);
  border-color: #38bdf8;
  color: #bae6fd;
}

/* Checkboxes */
.pg-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 1.25rem;
}
.pg-checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color 0.2s;
}
.pg-checkbox-label:hover {
  color: var(--text-primary);
}
.pg-checkbox {
  width: 16px;
  height: 16px;
  accent-color: var(--accent);
  cursor: pointer;
}

/* Toggles & Visibility */
.pg-toggle-btn {
  background: none;
  border: none;
  color: #38bdf8;
  font-size: 0.85rem;
  cursor: pointer;
}
.pg-toggle-btn:hover {
  text-decoration: underline;
}
.fade-in {
  animation: fadeIn 0.3s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-5px); }
  to { opacity: 1; transform: translateY(0); }
}
.pg-advanced-hidden {
  text-align: center;
  padding: 1rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  color: var(--text-muted);
  font-size: 0.85rem;
}

/* Preview / Result Side */
.pg-preview-card {
  min-height: 500px;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}
.pg-generate-btn {
  width: 100%;
  padding: 1.1rem;
  background: linear-gradient(135deg, var(--accent) 0%, #10b981 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  box-shadow: 0 4px 12px rgba(37, 164, 100, 0.2);
}
.pg-generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 164, 100, 0.3);
}
.pg-generate-btn:disabled {
  background: var(--border);
  color: var(--text-muted);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* Empty State */
.empty-state {
  justify-content: center;
  align-items: center;
  padding: 2.5rem;
  text-align: center;
}
.empty-icon-wrapper {
  width: 64px;
  height: 64px;
  background: var(--accent-dim);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
}
.empty-icon {
  font-size: 2rem;
}
.empty-title {
  font-size: 1.25rem;
  color: var(--text-primary);
  margin: 0 0 0.5rem;
}
.empty-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 2rem;
}
.generate-actions {
  width: 100%;
  text-align: left;
}

/* Result State */
.result-state {
  height: calc(100vh - 120px);
  min-height: 600px;
  border-color: var(--accent);
}
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}
.result-title {
  font-size: 1rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}
.pg-reset-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 0.8rem;
  cursor: pointer;
}
.pg-reset-btn:hover { color: var(--text-primary); }

.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}
.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--border-subtle);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1.5rem;
}
@keyframes spin { 100% { transform: rotate(360deg); } }
.loading-title { margin: 0 0 0.5rem; font-size: 1.1rem; color: var(--text-primary); }
.loading-desc { font-size: 0.85rem; color: var(--text-secondary); }

.result-content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-primary);
}
.result-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  position: relative;
}
.copy-json-btn {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 0.4rem;
  border-radius: 6px;
  cursor: pointer;
  opacity: 0.5;
  transition: all 0.2s;
}
.copy-json-btn:hover { opacity: 1; border-color: var(--accent); }

.flex-col-area {
  display: flex;
  flex-direction: column;
}

.full-prompt-textarea {
  flex: 1;
  width: 100%;
  min-height: 400px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 1.25rem;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.95rem;
  line-height: 1.6;
  resize: none;
  outline: none;
  white-space: pre-wrap;
}
.full-prompt-textarea:focus {
  border-color: var(--accent);
}

.result-footer {
  padding: 1.25rem;
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-subtle);
  flex-shrink: 0;
}
.pg-copy-main-btn {
  width: 100%;
  padding: 0.85rem;
  background: var(--text-primary);
  color: var(--bg-primary);
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.1s;
}
.pg-copy-main-btn:active { transform: scale(0.98); }

.pg-save-kb-btn {
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-primary);
  font-family: inherit;
  font-weight: 600;
  font-size: 0.95rem;
  padding: 0.85rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}
.pg-save-kb-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--border-hover);
}

.result-footer-hint {
  text-align: center;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin: 0.75rem 0 0;
  width: 100%;
}

/* Modal styles */
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
  max-width: 500px;
  padding: 1.5rem;
  box-shadow: 0 10px 40px rgba(0,0,0,0.5);
  animation: modalPop 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modalPop {
  0% { transform: scale(0.95); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.kb-modal-title {
  margin: 0 0 1.5rem 0;
  font-size: 1.3rem;
  color: var(--text-primary);
}

.kb-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
}

.btn-save {
  background: var(--accent);
  border: none;
  color: #fff;
  padding: 0.6rem 1.5rem;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
}
.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Responsiveness */
@media (max-width: 900px) {
  .generator-layout {
    flex-direction: column;
  }
  .generator-sidebar { width: 100%; }
  .generator-main { width: 100%; position: static; }
  .result-state { min-height: 80vh; height: auto; }
}
</style>
