<template>
  <div class="mcp-card fade-up" @click="$router.push(`/mcp/${mcp.name}`)">
    <div class="mcp-card-header">
      <div class="mcp-icon">{{ mcp.display_name?.[0]?.toUpperCase() || '🔌' }}</div>
      <div class="mcp-meta">
        <div class="mcp-name">{{ mcp.display_name }}</div>
        <div class="mcp-slug">{{ mcp.author }}/{{ mcp.name }}</div>
      </div>
      <span v-if="mcp.is_verified" class="verified-badge" title="已驗證">✓</span>
    </div>

    <p class="mcp-desc">{{ mcp.description }}</p>

    <div class="mcp-footer">
      <div class="mcp-badges">
        <span class="transport-badge" :class="mcp.transport">
          <span class="badge-dot"></span>
          {{ transportLabel(mcp.transport) }}
        </span>
        <span v-if="mcp.category" class="cat-badge">
          {{ categoryIcon(mcp.category) }} {{ categoryLabel(mcp.category) }}
        </span>
      </div>
      <div class="mcp-installs">
        <span class="install-icon">⬇</span>
        {{ formatNum(mcp.installs) }}
      </div>
    </div>

    <!-- Local support badges -->
    <div class="local-badges" v-if="localTypes.length">
      <span v-for="t in localTypes" :key="t" class="local-badge" :class="t">
        {{ localIcon(t) }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ mcp: { type: Object, required: true } })

const localTypes = computed(() =>
  [...new Set((props.mcp.local_config || []).map(c => c.type))]
)

function transportLabel(t) {
  return { sse: 'Remote SSE', stdio: 'Stdio', http: 'HTTP' }[t] || t || 'Remote'
}

function localIcon(t) {
  return { docker: '🐳', python: '🐍', node: '🟢' }[t] || '📦'
}

function categoryIcon(cat) {
  const icons = {
    coding: '💻', web: '🌐', search: '🔍', data: '📊', database: '🗄️',
    ai: '🤖', productivity: '⚡', writing: '✍️', design: '🎨', devops: '🛠️',
    communication: '💬', maps: '📍', finance: '💰', science: '🧪',
    travel: '✈️', health: '🏥', other: '📦'
  }
  return icons[cat] || '🧩'
}

function categoryLabel(cat) {
  const labels = {
    coding: 'Coding', web: 'Web', search: 'Search', data: 'Data', database: 'Database',
    ai: 'AI', productivity: 'Productivity', writing: 'Writing', design: 'Design', devops: 'DevOps',
    communication: 'Comm', maps: 'Maps', finance: 'Finance', science: 'Science',
    travel: 'Travel', health: 'Health', other: 'Other'
  }
  return labels[cat] || cat
}

function formatNum(n) {
  if (!n) return '0'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k'
  return String(n)
}
</script>

<style scoped>
.mcp-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.1rem;
  cursor: pointer;
  transition: border-color 0.15s, transform 0.15s, box-shadow 0.15s;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.mcp-card:hover {
  border-color: #f97316;
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(249,115,22,0.12);
}

.mcp-card-header { display: flex; align-items: flex-start; gap: 0.75rem; }
.mcp-icon {
  width: 40px; height: 40px; border-radius: 10px;
  background: linear-gradient(135deg, rgba(249,115,22,0.2), rgba(251,146,60,0.1));
  border: 1px solid rgba(249,115,22,0.25);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.15rem; font-weight: 700; color: #f97316;
  flex-shrink: 0;
}
.mcp-meta { flex: 1; min-width: 0; }
.mcp-name { font-weight: 600; font-size: 0.92rem; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mcp-slug { font-size: 0.72rem; color: var(--text-muted); }
.verified-badge { font-size: 0.7rem; background: rgba(249,115,22,0.15); color: #f97316; border: 1px solid rgba(249,115,22,0.3); border-radius: 10px; padding: 1px 6px; }

.mcp-desc {
  font-size: 0.82rem; color: var(--text-muted); line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  margin: 0;
}

.mcp-footer { display: flex; justify-content: space-between; align-items: center; }
.mcp-badges { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.transport-badge {
  display: flex; align-items: center; gap: 4px;
  font-size: 0.7rem; padding: 2px 7px; border-radius: 8px;
  background: rgba(249,115,22,0.1); color: #f97316;
  border: 1px solid rgba(249,115,22,0.2);
}
.badge-dot { width: 5px; height: 5px; border-radius: 50%; background: #f97316; }
.cat-badge { font-size: 0.68rem; color: var(--text-muted); background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 1px 6px; }
.mcp-installs { font-size: 0.75rem; color: var(--text-muted); display: flex; align-items: center; gap: 3px; }
.install-icon { font-size: 0.7rem; }

.local-badges { display: flex; gap: 4px; }
.local-badge { font-size: 0.8rem; }
</style>
