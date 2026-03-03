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
        <div class="code-block-header">
          <span>SKILL.md</span>
        </div>
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
            <div>
              <div class="cli-label">安裝 CLI</div>
              <div class="code-block">pip install agentskills</div>
            </div>
          </div>
          <div class="cli-step">
            <span class="cli-num">2</span>
            <div>
              <div class="cli-label">登入 Registry</div>
              <div class="code-block">agentskills login</div>
            </div>
          </div>
          <div class="cli-step">
            <span class="cli-num">3</span>
            <div>
              <div class="cli-label">推送 Skill</div>
              <div class="code-block">agentskills push ./my-skill</div>
            </div>
          </div>
        </div>

        <div class="step-actions">
          <button class="btn-ghost" @click="step = 0">← 上一步</button>
          <button class="btn-primary" @click="step = 2">也想用表單發布 →</button>
        </div>
      </div>

      <!-- Step 2: Web Form Push -->
      <div v-if="step === 2" class="step-content card fade-up">
        <h2>表單發布</h2>
        <p class="step-desc">直接貼上 SKILL.md 內容：</p>

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
          <div class="form-row full">
            <label>標籤（逗號分隔）</label>
            <input v-model="form.tagsRaw" class="form-input" placeholder="search, web, productivity" />
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
import { ref, reactive } from 'vue'
import { skillsApi } from '@/api'

const step = ref(0)
const submitting = ref(false)
const submitError = ref('')
const submitOk = ref(false)

const STEPS = [
  { id: 'structure', label: 'Bundle 結構' },
  { id: 'cli', label: 'CLI 發布' },
  { id: 'form', label: '表單發布' },
]

const form = reactive({
  name: '', version: '1.0.0', description: '', author: '',
  license: 'MIT', tagsRaw: '', skill_md: ''
})

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
      skill_md: form.skill_md,
    })
    submitOk.value = true
    Object.assign(form, { name:'', version:'1.0.0', description:'', author:'', license:'MIT', tagsRaw:'', skill_md:'' })
  } catch (e) {
    submitError.value = e.response?.data?.error || '發布失敗，請稍後再試'
  } finally {
    submitting.value = false
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
.error-msg { color: #e05252; font-size: 0.85rem; margin-top: 0.5rem; }
.success-msg { color: var(--accent); font-size: 0.9rem; margin-top: 0.5rem; font-weight: 500; }

/* New Styles for Step 0 */
.structure-box {
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.25rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  line-height: 1.6;
  margin: 1rem 0;
}
.folder-name { color: #5eb5f7; font-weight: 600; }
.file-name { color: var(--accent); font-weight: 600; }
.comment { color: var(--text-muted); margin-left: 1rem; font-style: italic; }

.code-block-header {
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-bottom: none;
  border-radius: 8px 8px 0 0;
  padding: 0.4rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
}
.publish-page .code-block {
  border-radius: 0 0 8px 8px;
  margin-top: 0;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}
</style>
