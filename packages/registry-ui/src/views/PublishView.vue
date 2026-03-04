<template>
  <div class="publish-page">
    <div class="publish-inner">
      <h1 class="page-title">🚀 發布 Skill</h1>
      <p class="page-sub">將你的 Agent Skill 分享給社群</p>

      <!-- Step tabs -->
      <div class="steps">
        <div v-for="(s, i) in STEPS" :key="s.id" class="step" :class="{ active: step === i, done: step > i }">
          <div class="step-num">{{ step > i ? '✓' : i + 1 }}</div>
          <span>{{ s.label }}</span>
        </div>
      </div>

      <!-- Step 0: Bundle Structure -->
      <div v-if="step === 0" class="step-content card fade-up">
        <h2>1. 準備 Skill Bundle 結構</h2>
        <p class="step-desc">請確保您的 Skill 資料夾符合以下標準目錄結構：</p>
        <div class="structure-box">
          <div class="structure-line"><span class="folder-name">my-skill/</span></div>
          <div class="structure-line">├── <span class="file-name">SKILL.md</span> <span class="comment">← 必填：YAML 前言 + Markdown 指令</span></div>
          <div class="structure-line">├── <span class="folder-name">scripts/</span> <span class="comment">← 選填：Agent 可執行的腳本</span></div>
          <div class="structure-line">├── <span class="folder-name">references/</span> <span class="comment">← 選填：RAG / 參考文件</span></div>
          <div class="structure-line">└── <span class="folder-name">assets/</span> <span class="comment">← 選填：靜態資源</span></div>
        </div>
        <h3>SKILL.md 範本</h3>
        <p class="step-desc">這是最核心的檔案，定義了技能的元數據與操作邏輯：</p>
        <div class="code-block-header"><span>SKILL.md</span></div>
        <pre class="code-block">---
name: "my-cool-tool"
description: "簡短描述這個 Skill 的功能"
version: "1.0.0"
author: "your-name"
tags: ["tag1", "tag2"]
license: "MIT"
---

# My Skill Name

在這裡撰寫 AI 的操作指令...

## When to Use
- 描述何時該啟用此技能...</pre>
        <div class="step-actions">
          <button class="btn-primary" @click="step = 1">準備好了，下一步 →</button>
        </div>
      </div>

      <!-- Step 1: CLI Push -->
      <div v-if="step === 1" class="step-content card fade-up">
        <h2>使用 CLI 發布</h2>
        <p class="step-desc">透過 agentskills CLI 打包並推送到 Registry：</p>
        <div class="cli-steps">
          <div class="cli-step">
            <span class="cli-num">1</span>
            <div><div class="cli-label">安裝 CLI</div><div class="code-block">pip install agentskills</div></div>
          </div>
          <div class="cli-step">
            <span class="cli-num">2</span>
            <div><div class="cli-label">登入 Registry</div><div class="code-block">agentskills login</div></div>
          </div>
          <div class="cli-step">
            <span class="cli-num">3</span>
            <div><div class="cli-label">推送 Skill</div><div class="code-block">agentskills push ./my-skill</div></div>
          </div>
        </div>
        <div class="step-actions">
          <button class="btn-ghost" @click="step = 0">← 上一步</button>
          <button class="btn-outline" @click="step = 2">📦 從 GitHub 匯入 →</button>
          <button class="btn-primary" @click="step = 3">也想用表單發布 →</button>
        </div>
      </div>

      <!-- Step 2: GitHub Import -->
      <div v-if="step === 2" class="step-content card fade-up">
        <div class="github-import-header">
          <div class="github-import-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
            </svg>
          </div>
          <div>
            <h2>從 GitHub 匯入 Skill</h2>
            <p class="step-desc">貼上含有 SKILL.md 的 GitHub 資料夾連結，系統將自動讀取並匯入。</p>
          </div>
        </div>

        <div class="github-form">
          <div class="form-row full">
            <label>GitHub URL <span class="required">*</span> <span class="label-hint">— 填寫含有 SKILL.md 的資料夾網址</span></label>
            <div class="url-input-wrap">
              <input v-model="githubUrl" class="form-input" placeholder="https://github.com/user/repo/tree/main/my-skill" id="github-url-input" @keyup.enter="fetchFromGithub" />
              <button class="btn-fetch" :disabled="githubFetching || !githubUrl.trim()" @click="fetchFromGithub">
                {{ githubFetching ? '讀取中…' : '🔍 讀取' }}
              </button>
            </div>
            <p class="field-hint">支援格式：<code>https://github.com/user/repo/tree/branch/path/to/skill</code> 或直接指向 SKILL.md</p>
          </div>

          <div v-if="githubError" class="error-msg github-error">⚠️ {{ githubError }}</div>

          <template v-if="githubPreview">
            <div class="preview-divider"><span>✅ 讀取成功 — 預覽並確認資訊</span></div>

            <div class="form-grid">
              <div class="form-row">
                <label>Skill 名稱 <span class="required">*</span></label>
                <input v-model="githubForm.name" class="form-input" placeholder="my-skill" />
              </div>
              <div class="form-row">
                <label>版本 <span class="required">*</span></label>
                <input v-model="githubForm.version" class="form-input" placeholder="1.0.0" />
              </div>
              <div class="form-row full">
                <label>描述 <span class="required">*</span></label>
                <input v-model="githubForm.description" class="form-input" />
              </div>
              <div class="form-row">
                <label>作者 <span class="required">*</span></label>
                <input v-model="githubForm.author" class="form-input" placeholder="your-name" />
              </div>
              <div class="form-row">
                <label>License</label>
                <input v-model="githubForm.license" class="form-input" placeholder="MIT" />
              </div>

              <!-- 分類欄位（GitHub 表單） -->
              <div class="form-row">
                <label>分類</label>
                <div class="field-with-ai">
                  <select v-model="githubForm.category" class="form-input form-select">
                    <option value="">— 未分類 —</option>
                    <option v-for="cat in CATEGORIES" :key="cat.id" :value="cat.id">
                      {{ cat.icon }} {{ cat.label }}
                    </option>
                  </select>
                  <button class="btn-ai-gen" :disabled="aiClassifyingGithub" @click="aiClassifyGithub" title="AI 自動判斷分類">
                    {{ aiClassifyingGithub ? '⏳' : '🤖 AI' }}
                  </button>
                </div>
              </div>

              <!-- 標籤欄位（GitHub 表單） -->
              <div class="form-row full">
                <label>標籤</label>
                <div class="field-with-ai">
                  <input v-model="githubForm.tagsRaw" class="form-input" placeholder="search, web, productivity" />
                  <button class="btn-ai-gen" :disabled="aiTaggingGithub" @click="aiGenerateTagsGithub" title="AI 自動生成標籤">
                    {{ aiTaggingGithub ? '⏳' : '🤖 AI' }}
                  </button>
                </div>
                <!-- 現有熱門標籤 chips -->
                <div class="tag-chips" v-if="availableTags.length">
                  <span class="chips-label">現有標籤：</span>
                  <span
                    v-for="t in availableTags.slice(0, 20)"
                    :key="t.tag"
                    class="tag-chip"
                    :class="{ active: githubTagsSet.has(t.tag) }"
                    @click="toggleGithubTag(t.tag)"
                  >{{ t.tag }}</span>
                </div>
              </div>
            </div>

            <!-- SKILL.md preview -->
            <div class="skillmd-preview-wrap">
              <div class="skillmd-preview-header"><span>📄 SKILL.md 內容預覽</span></div>
              <pre class="skillmd-preview">{{ githubForm.skill_md }}</pre>
            </div>

            <div v-if="githubSubmitError" class="error-msg">{{ githubSubmitError }}</div>
            <div v-if="githubSubmitOk" class="success-msg">🎉 Skill 匯入成功！</div>
          </template>
        </div>

        <div class="step-actions">
          <button class="btn-ghost" @click="step = 1">← 上一步</button>
          <button v-if="githubPreview" class="btn-primary" :disabled="githubSubmitting" @click="submitGithubImport">
            {{ githubSubmitting ? '發布中…' : '🚀 確認發布' }}
          </button>
        </div>
      </div>

      <!-- Step 3: Web Form Push -->
      <div v-if="step === 3" class="step-content card fade-up">
        <h2>表單發布</h2>
        <p class="step-desc">填寫技能資訊並貼上 SKILL.md 內容：</p>

        <div class="form-grid">
          <div class="form-row">
            <label>Skill 名稱 <span class="required">*</span></label>
            <input v-model="form.name" class="form-input" placeholder="my-skill（小寫英文、連字符）" id="publish-name" />
          </div>
          <div class="form-row">
            <label>版本 <span class="required">*</span></label>
            <input v-model="form.version" class="form-input" placeholder="1.0.0" />
          </div>
          <div class="form-row full">
            <label>描述 <span class="required">*</span></label>
            <input v-model="form.description" class="form-input" placeholder="一句話描述這個 Skill 的功能" />
          </div>
          <div class="form-row">
            <label>作者 <span class="required">*</span></label>
            <input v-model="form.author" class="form-input" placeholder="your-name" />
          </div>
          <div class="form-row">
            <label>License</label>
            <input v-model="form.license" class="form-input" placeholder="MIT" />
          </div>

          <!-- 分類欄位（表單發布） -->
          <div class="form-row">
            <label>分類</label>
            <div class="field-with-ai">
              <select v-model="form.category" class="form-input form-select">
                <option value="">— 未分類 —</option>
                <option v-for="cat in CATEGORIES" :key="cat.id" :value="cat.id">
                  {{ cat.icon }} {{ cat.label }}
                </option>
              </select>
              <button class="btn-ai-gen" :disabled="aiClassifyingForm" @click="aiClassifyForm" title="AI 自動判斷分類">
                {{ aiClassifyingForm ? '⏳' : '🤖 AI' }}
              </button>
            </div>
          </div>

          <!-- 標籤欄位（表單發布） -->
          <div class="form-row full">
            <label>標籤（逗號分隔）</label>
            <div class="field-with-ai">
              <input v-model="form.tagsRaw" class="form-input" placeholder="search, web, productivity" />
              <button class="btn-ai-gen" :disabled="aiTaggingForm" @click="aiGenerateTagsForm" title="AI 自動生成標籤">
                {{ aiTaggingForm ? '⏳' : '🤖 AI' }}
              </button>
            </div>
            <!-- 現有熱門標籤 chips -->
            <div class="tag-chips" v-if="availableTags.length">
              <span class="chips-label">現有標籤：</span>
              <span
                v-for="t in availableTags.slice(0, 20)"
                :key="t.tag"
                class="tag-chip"
                :class="{ active: formTagsSet.has(t.tag) }"
                @click="toggleFormTag(t.tag)"
              >{{ t.tag }}</span>
            </div>
          </div>

          <div class="form-row full">
            <label>SKILL.md 內容 <span class="required">*</span></label>
            <textarea v-model="form.skill_md" class="form-textarea" rows="12" placeholder="貼上 SKILL.md 的完整內容…" />
          </div>
        </div>

        <div v-if="submitError" class="error-msg">{{ submitError }}</div>
        <div v-if="submitOk" class="success-msg">🎉 Skill 發布成功！</div>

        <div class="step-actions">
          <button class="btn-ghost" @click="step = 1">← 上一步</button>
          <button class="btn-primary" :disabled="submitting" @click="submitForm">
            {{ submitting ? '發布中…' : '🚀 發布' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { skillsApi } from '@/api'

const step = ref(0)
const submitting = ref(false)
const submitError = ref('')
const submitOk = ref(false)

const STEPS = [
  { id: 'structure', label: 'Bundle 結構' },
  { id: 'cli',       label: 'CLI 發布' },
  { id: 'github',    label: 'GitHub 匯入' },
  { id: 'form',      label: '表單發布' },
]

// ── 分類定義（與後端同步）──
const CATEGORIES = [
  { id: 'coding',       icon: '💻', label: '程式開發' },
  { id: 'web',          icon: '🌐', label: 'Web / UI' },
  { id: 'data',         icon: '📊', label: '資料分析' },
  { id: 'writing',      icon: '✍️',  label: '文案 / 文件' },
  { id: 'ai',           icon: '🤖', label: 'AI / Agent' },
  { id: 'design',       icon: '🎨', label: '設計 / 創作' },
  { id: 'productivity', icon: '⚡', label: '效率工具' },
  { id: 'devops',       icon: '🛠️', label: 'DevOps' },
]

// ── 現有標籤（從後端載入）──
const availableTags = ref([])
onMounted(async () => {
  try {
    const res = await skillsApi.tags()
    availableTags.value = res.data || []
  } catch {}
})

// ── 表單發布 ──
const aiTaggingForm = ref(false)
const aiClassifyingForm = ref(false)

const form = reactive({
  name: '', version: '1.0.0', description: '', author: '',
  license: 'MIT', tagsRaw: '', skill_md: '', category: ''
})

// 表單 tag 集合（用於 chip active 狀態）
const formTagsSet = computed(() => {
  return new Set(form.tagsRaw.split(',').map(t => t.trim()).filter(Boolean))
})

function toggleFormTag(tag) {
  const current = form.tagsRaw.split(',').map(t => t.trim()).filter(Boolean)
  if (current.includes(tag)) {
    form.tagsRaw = current.filter(t => t !== tag).join(', ')
  } else {
    form.tagsRaw = [...current, tag].join(', ')
  }
}

/** AI 自動生成標籤（表單） */
async function aiGenerateTagsForm() {
  if (!form.name && !form.description && !form.skill_md) {
    alert('請先填寫技能名稱或描述，才能 AI 生成標籤')
    return
  }
  aiTaggingForm.value = true
  try {
    const tags = clientSideGenerateTags({
      name: form.name, description: form.description, skill_md: form.skill_md
    })
    form.tagsRaw = tags.join(', ')
  } finally {
    aiTaggingForm.value = false
  }
}

/** AI 自動判斷分類（表單） */
async function aiClassifyForm() {
  if (!form.name && !form.description) {
    alert('請先填寫技能名稱或描述，才能 AI 自動分類')
    return
  }
  aiClassifyingForm.value = true
  try {
    const cat = clientSideClassify({
      name: form.name, description: form.description,
      tags: form.tagsRaw.split(',').map(t => t.trim()), skill_md: form.skill_md
    })
    form.category = cat || ''
  } finally {
    aiClassifyingForm.value = false
  }
}

async function submitForm() {
  submitError.value = ''
  submitOk.value = false
  if (!form.name || !form.version || !form.description || !form.author || !form.skill_md) {
    submitError.value = '請填寫所有必填欄位'
    return
  }
  submitting.value = true
  try {
    await skillsApi.push({
      name: form.name.trim(),
      version: form.version.trim(),
      description: form.description.trim(),
      author: form.author.trim(),
      license: form.license.trim(),
      tags: form.tagsRaw.split(',').map(t => t.trim()).filter(Boolean),
      category: form.category || undefined,
      skill_md: form.skill_md,
    })
    submitOk.value = true
    Object.assign(form, { name:'', version:'1.0.0', description:'', author:'', license:'MIT', tagsRaw:'', skill_md:'', category:'' })
  } catch (e) {
    submitError.value = e.response?.data?.error || '發布失敗，請稍後再試'
  } finally {
    submitting.value = false
  }
}

// ── GitHub 匯入 ──
const githubUrl = ref('')
const githubFetching = ref(false)
const githubError = ref('')
const githubPreview = ref(false)
const githubSubmitting = ref(false)
const githubSubmitError = ref('')
const githubSubmitOk = ref(false)
const aiTaggingGithub = ref(false)
const aiClassifyingGithub = ref(false)

const githubForm = reactive({
  name: '', version: '1.0.0', description: '', author: '',
  license: 'MIT', tagsRaw: '', skill_md: '', repository: '', category: ''
})

// GitHub tag 集合
const githubTagsSet = computed(() => {
  return new Set(githubForm.tagsRaw.split(',').map(t => t.trim()).filter(Boolean))
})

function toggleGithubTag(tag) {
  const current = githubForm.tagsRaw.split(',').map(t => t.trim()).filter(Boolean)
  if (current.includes(tag)) {
    githubForm.tagsRaw = current.filter(t => t !== tag).join(', ')
  } else {
    githubForm.tagsRaw = [...current, tag].join(', ')
  }
}

/** AI 自動生成標籤（GitHub 表單） */
async function aiGenerateTagsGithub() {
  if (!githubForm.name && !githubForm.description && !githubForm.skill_md) {
    alert('請先取得 GitHub 內容後才能 AI 生成標籤')
    return
  }
  aiTaggingGithub.value = true
  try {
    const tags = clientSideGenerateTags({
      name: githubForm.name, description: githubForm.description, skill_md: githubForm.skill_md
    })
    githubForm.tagsRaw = tags.join(', ')
  } finally {
    aiTaggingGithub.value = false
  }
}

/** AI 自動判斷分類（GitHub 表單） */
async function aiClassifyGithub() {
  aiClassifyingGithub.value = true
  try {
    const cat = clientSideClassify({
      name: githubForm.name, description: githubForm.description,
      tags: githubForm.tagsRaw.split(',').map(t => t.trim()), skill_md: githubForm.skill_md
    })
    githubForm.category = cat || ''
  } finally {
    aiClassifyingGithub.value = false
  }
}

// ── 客戶端啟發式 AI 邏輯 ──────────────────────────────────────────

const TAG_KEYWORDS = [
  ['python',      /python/],
  ['javascript',  /javascript|js\b|node/],
  ['typescript',  /typescript|ts\b/],
  ['web',         /web|html|css|frontend/],
  ['browser',     /browser|chrome|playwright|selenium/],
  ['automation',  /automat|macro|script/],
  ['ai',          /\bai\b|llm|gpt|gemini|claude/],
  ['rag',         /rag|retriev|knowledge.base|vector/],
  ['mcp',         /\bmcp\b|model.context.protocol/],
  ['testing',     /test|tdd|jest|pytest|vitest/],
  ['git',         /\bgit\b|github|version.control/],
  ['docker',      /docker|container|kubernetes/],
  ['data',        /\bdata\b|analytics|excel|csv|xlsx/],
  ['pdf',         /\bpdf\b/],
  ['word',        /\bword\b|docx|\.docx/],
  ['pptx',        /pptx|powerpoint|slide/],
  ['design',      /design|art|image|graphic|poster/],
  ['writing',     /writ|doc|documentation|readme/],
  ['productivity',/product|workflow|task|planning/],
  ['code',        /code|coding|program|refactor|review/],
  ['search',      /search|web.search|information/],
  ['slack',       /slack/],
  ['email',       /email|mail/],
  ['image',       /image|png|jpg|svg/],
  ['api',         /\bapi\b|rest|endpoint/],
  ['sql',         /\bsql\b|database|mysql|postgres/],
]

function clientSideGenerateTags({ name = '', description = '', skill_md = '' }) {
  const text = `${name} ${description} ${skill_md}`.toLowerCase()
  const result = []
  for (const [tag, re] of TAG_KEYWORDS) {
    if (re.test(text)) result.push(tag)
    if (result.length >= 6) break
  }
  return result.length ? result : ['skill', 'agent']
}

function clientSideClassify({ name = '', description = '', tags = [], skill_md = '' }) {
  const text = [name, description, skill_md, ...tags].join(' ').toLowerCase()
  const rules = [
    ['devops',       /devops|docker|deploy|kubernetes|cloud|infra|ci.?cd/],
    ['data',         /\bdata\b|analytics|excel|xlsx|csv|sql|spreadsheet/],
    ['writing',      /\bdoc\b|docs|markdown|writing|report|pdf|word|docx|pptx|slide|readme/],
    ['web',          /web|html|css|frontend|browser|ui\b|ux\b|playwright|webapp|artifact/],
    ['design',       /design|art\b|image|graphic|generative|algorithmic|poster|brand|theme|gif/],
    ['productivity', /product|slack|email|meeting|planning|internal.comm/],
    ['ai',           /\bai\b|llm|rag|knowledge.base|mcp|vector|embed|prompt/],
    ['coding',       /code|coding|program|test|debug|refactor|review|\bgit\b|javascript|python|typescript|script|macro/],
  ]
  for (const [id, re] of rules) {
    if (re.test(text)) return id
  }
  return null
}

// ── URL 解析與 SKILL.md 取得 ──────────────────────────────────────

function toRawSkillMdUrl(url) {
  try {
    const u = new URL(url.trim())
    if (u.hostname !== 'github.com') return null
    const parts = u.pathname.split('/').filter(Boolean)
    if (parts.length < 2) return null
    const [user, repo] = parts
    if (parts.length === 2) return `https://raw.githubusercontent.com/${user}/${repo}/main/SKILL.md`
    const treeOrBlob = parts[2]
    const branch = parts[3] || 'main'
    const pathParts = parts.slice(4)
    if (treeOrBlob === 'blob') return `https://raw.githubusercontent.com/${user}/${repo}/${branch}/${pathParts.join('/')}`
    const skillPath = [...pathParts, 'SKILL.md'].join('/')
    return `https://raw.githubusercontent.com/${user}/${repo}/${branch}/${skillPath}`
  } catch { return null }
}

function parseFrontmatter(content) {
  const match = content.match(/^---\s*\n([\s\S]*?)\n---/)
  if (!match) return {}
  const yaml = match[1]
  const result = {}
  for (const line of yaml.split('\n')) {
    const m = line.match(/^(\w+):\s*(.+)/)
    if (!m) continue
    const [, key, val] = m
    const trimmed = val.trim().replace(/^["']|["']$/g, '')
    if (key === 'tags') {
      result.tags = val.replace(/[\[\]]/g, '').split(',').map(t => t.trim().replace(/^["']|["']$/g, '')).filter(Boolean)
    } else {
      result[key] = trimmed
    }
  }
  return result
}

async function fetchFromGithub() {
  githubError.value = ''
  githubPreview.value = false
  githubSubmitOk.value = false
  githubSubmitError.value = ''
  const rawUrl = toRawSkillMdUrl(githubUrl.value)
  if (!rawUrl) { githubError.value = '無法解析 GitHub URL，請確認格式正確'; return }
  githubFetching.value = true
  try {
    const res = await fetch(rawUrl)
    if (!res.ok) {
      githubError.value = res.status === 404 ? '找不到 SKILL.md，請確認路徑與分支名稱正確' : `讀取失敗（HTTP ${res.status}）`
      return
    }
    const content = await res.text()
    const meta = parseFrontmatter(content)
    Object.assign(githubForm, {
      name:        meta.name        || '',
      version:     meta.version     || '1.0.0',
      description: meta.description || '',
      author:      meta.author      || '',
      license:     meta.license     || 'MIT',
      tagsRaw:     (meta.tags || []).join(', '),
      skill_md:    content,
      repository:  githubUrl.value.trim(),
      category:    '',
    })
    // 匯入後自動 AI 分類
    githubForm.category = clientSideClassify({
      name: githubForm.name, description: githubForm.description,
      tags: meta.tags || [], skill_md: content
    }) || ''
    githubPreview.value = true
  } catch {
    githubError.value = '網路錯誤，請確認 URL 是否正確，或稍後再試'
  } finally {
    githubFetching.value = false
  }
}

async function submitGithubImport() {
  githubSubmitError.value = ''
  githubSubmitOk.value = false
  const { name, version, description, author, skill_md, license, tagsRaw, repository, category } = githubForm
  if (!name || !version || !description || !author || !skill_md) { githubSubmitError.value = '請填寫所有必填欄位'; return }
  githubSubmitting.value = true
  try {
    await skillsApi.push({
      name: name.trim(), version: version.trim(), description: description.trim(),
      author: author.trim(), license: license.trim(),
      tags: tagsRaw.split(',').map(t => t.trim()).filter(Boolean),
      category: category || undefined,
      skill_md, repository,
    })
    githubSubmitOk.value = true
    githubPreview.value = false
    githubUrl.value = ''
  } catch (e) {
    githubSubmitError.value = e.response?.data?.error || '發布失敗，請稍後再試'
  } finally {
    githubSubmitting.value = false
  }
}
</script>

<style scoped>
.publish-page { max-width: 820px; margin: 0 auto; padding: 2.5rem 1.5rem; }
.page-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; font-weight: 700; margin-bottom: 0.25rem; }
.page-sub { color: var(--text-muted); margin-bottom: 2rem; }

/* Steps nav */
.steps { display: flex; gap: 0; margin-bottom: 2rem; border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
.step { display: flex; align-items: center; gap: 0.6rem; padding: 0.7rem 1.25rem; flex: 1; font-size: 0.85rem; color: var(--text-muted); border-right: 1px solid var(--border); transition: background 0.15s; }
.step:last-child { border-right: none; }
.step.active { background: var(--accent-dim); color: var(--accent); font-weight: 600; }
.step.done { color: var(--accent); }
.step-num { width: 22px; height: 22px; border-radius: 50%; background: var(--bg-secondary); border: 1px solid var(--border); display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 600; flex-shrink: 0; }
.step.active .step-num { background: var(--accent); border-color: var(--accent); color: #fff; }

/* Step content */
.step-content { padding: 2rem; }
.step-content h2 { font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; margin: 0 0 0.5rem; }
.step-content h3 { font-size: 0.95rem; font-weight: 600; margin: 1.25rem 0 0.5rem; }
.step-desc { color: var(--text-muted); font-size: 0.88rem; margin-bottom: 1rem; }
.step-actions { display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.5rem; }

/* CLI Steps */
.cli-steps { display: flex; flex-direction: column; gap: 1rem; margin: 1rem 0; }
.cli-step { display: flex; gap: 1rem; align-items: flex-start; }
.cli-num { width: 28px; height: 28px; border-radius: 50%; background: var(--accent-dim); border: 1px solid rgba(37,164,100,0.3); color: var(--accent); font-size: 0.85rem; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 4px; }
.cli-label { font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.35rem; }

/* Form */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-row { display: flex; flex-direction: column; gap: 0.35rem; }
.form-row.full { grid-column: 1 / -1; }
.form-row label { font-size: 0.82rem; color: var(--text-secondary); font-weight: 500; }
.required { color: #e05252; }
.form-input, .form-textarea {
  padding: 0.55rem 0.85rem;
  background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px;
  color: var(--text-primary); font-size: 0.88rem; font-family: inherit; outline: none;
  transition: border-color 0.15s;
}
.form-input:focus, .form-textarea:focus { border-color: var(--accent); }
.form-textarea { resize: vertical; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; }
.form-select { appearance: none; cursor: pointer; }
.error-msg { color: #e05252; font-size: 0.85rem; margin-top: 0.5rem; }
.success-msg { color: var(--accent); font-size: 0.9rem; margin-top: 0.5rem; font-weight: 500; }

/* AI 欄位包裹 */
.field-with-ai { display: flex; gap: 0.5rem; align-items: stretch; }
.field-with-ai .form-input { flex: 1; }
.btn-ai-gen {
  padding: 0 0.75rem;
  border-radius: 8px;
  border: 1px solid rgba(37,164,100,0.4);
  background: var(--accent-dim);
  color: var(--accent);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
  flex-shrink: 0;
}
.btn-ai-gen:hover:not(:disabled) { background: var(--accent); color: #000; }
.btn-ai-gen:disabled { opacity: 0.5; cursor: not-allowed; }

/* 現有標籤 chips */
.tag-chips { display: flex; flex-wrap: wrap; gap: 0.35rem; align-items: center; margin-top: 0.5rem; }
.chips-label { font-size: 0.72rem; color: var(--text-muted); white-space: nowrap; margin-right: 0.2rem; }
.tag-chip {
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: var(--bg-secondary);
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.12s;
}
.tag-chip:hover { border-color: var(--accent); color: var(--accent); }
.tag-chip.active { background: var(--accent-dim); border-color: var(--accent); color: var(--accent); }

/* Structure box */
.structure-box {
  background: var(--bg-primary); border: 1px solid var(--border); border-radius: 8px;
  padding: 1.25rem; font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem; line-height: 1.6; margin: 1rem 0;
}
.folder-name { color: #5eb5f7; font-weight: 600; }
.file-name { color: var(--accent); font-weight: 600; }
.comment { color: var(--text-muted); margin-left: 1rem; font-style: italic; }
.code-block-header {
  background: var(--bg-primary); border: 1px solid var(--border); border-bottom: none;
  border-radius: 8px 8px 0 0; padding: 0.4rem 1rem;
  font-size: 0.75rem; font-weight: 600; color: var(--text-muted);
}
.publish-page .code-block {
  border-radius: 0 0 8px 8px; margin-top: 0; white-space: pre-wrap;
  word-break: break-word; line-height: 1.6; margin-bottom: 1.5rem;
}

/* GitHub Import */
.github-import-header {
  display: flex; align-items: flex-start; gap: 1rem; margin-bottom: 1.5rem;
  padding-bottom: 1.25rem; border-bottom: 1px solid var(--border-subtle);
}
.github-import-icon {
  width: 52px; height: 52px; border-radius: 12px; background: var(--bg-secondary);
  border: 1px solid var(--border); display: flex; align-items: center;
  justify-content: center; color: var(--text-secondary); flex-shrink: 0;
}
.github-import-header h2 { margin: 0 0 0.25rem; }
.github-import-header .step-desc { margin: 0; }
.github-form { display: flex; flex-direction: column; gap: 1rem; }
.url-input-wrap { display: flex; gap: 0.6rem; }
.url-input-wrap .form-input { flex: 1; }
.btn-fetch {
  padding: 0.55rem 1.1rem; border-radius: 8px; font-size: 0.88rem; font-weight: 600;
  background: var(--accent-dim); color: var(--accent); border: 1px solid rgba(37,164,100,0.35);
  cursor: pointer; white-space: nowrap; transition: all 0.15s;
}
.btn-fetch:hover:not(:disabled) { background: rgba(37,164,100,0.2); }
.btn-fetch:disabled { opacity: 0.5; cursor: not-allowed; }
.field-hint { font-size: 0.78rem; color: var(--text-muted); margin-top: 0.3rem; margin-bottom: 0; }
.field-hint code { font-family: 'JetBrains Mono', monospace; background: var(--bg-secondary); padding: 1px 5px; border-radius: 4px; font-size: 0.76rem; }
.label-hint { color: var(--text-muted); font-weight: 400; font-size: 0.78rem; }
.github-error { padding: 0.65rem 1rem; background: rgba(224,82,82,0.08); border: 1px solid rgba(224,82,82,0.25); border-radius: 8px; }
.preview-divider { display: flex; align-items: center; gap: 0.75rem; color: var(--accent); font-size: 0.82rem; font-weight: 600; margin: 0.5rem 0; }
.preview-divider::before, .preview-divider::after { content: ''; flex: 1; height: 1px; background: rgba(37,164,100,0.2); }
.skillmd-preview-wrap { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.skillmd-preview-header { background: var(--bg-secondary); border-bottom: 1px solid var(--border); padding: 0.4rem 1rem; font-size: 0.78rem; font-weight: 600; color: var(--text-muted); }
.skillmd-preview { margin: 0; padding: 1rem; background: var(--bg-primary); font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; line-height: 1.6; max-height: 250px; overflow-y: auto; white-space: pre-wrap; word-break: break-word; color: var(--text-secondary); }
.btn-outline { padding: 0.55rem 1.1rem; border-radius: 8px; font-size: 0.88rem; font-weight: 600; background: transparent; color: var(--accent); border: 1px solid rgba(37,164,100,0.45); cursor: pointer; transition: all 0.15s; }
.btn-outline:hover { background: var(--accent-dim); }
</style>
