<template>
  <RouterLink :to="`/skills/${skill.name}`" class="skill-card card">
    <div class="card-header">
      <div class="skill-icon">{{ getIcon(skill.tags) }}</div>
      <div class="skill-meta">
        <h3 class="skill-name">{{ skill.name }}</h3>
        <span class="skill-author">@{{ skill.author }}</span>
      </div>
      <span class="skill-version">v{{ skill.latest_version }}</span>
    </div>

    <p class="skill-desc">{{ skill.description }}</p>

    <div class="card-footer">
      <div class="skill-tags">
        <span
          v-for="tag in (skill.tags || []).slice(0, 4)"
          :key="tag"
          class="tag clickable-tag"
          @click.stop.prevent="filterByTag(tag)"
        >
          {{ tag }}
        </span>
      </div>
      <div class="skill-stats">
        <span class="stat">⬇ {{ formatNum(skill.downloads) }}</span>
      </div>
    </div>
  </RouterLink>
</template>

<script setup>
const props = defineProps({
  skill: { type: Object, required: true }
})

import { useRouter } from 'vue-router'
const router = useRouter()

const TAG_ICONS = {
  search: '🔍', web: '🌐', code: '💻', review: '🔎', git: '🌿',
  documentation: '📄', testing: '🧪', productivity: '⚡', ai: '🤖',
  security: '🔒', devops: '🚀', automation: '⚙️', writing: '✍️',
}

function filterByTag(tag) {
  router.push({ path: '/skills', query: { tags: tag } })
}

function getIcon(tags = []) {
  for (const tag of tags) {
    if (TAG_ICONS[tag]) return TAG_ICONS[tag]
  }
  return '🧩'
}

function formatNum(n) {
  if (!n) return '0'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k'
  return n.toString()
}
</script>

<style scoped>
.skill-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1.25rem;
  cursor: pointer;
  text-decoration: none;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.skill-icon {
  width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem;
  background: var(--accent-dim);
  border-radius: 10px;
  flex-shrink: 0;
}
.skill-meta { flex: 1; min-width: 0; }
.skill-name {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.97rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.skill-author { font-size: 0.78rem; color: var(--text-muted); }
.skill-version {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  color: var(--accent);
  background: var(--accent-dim);
  border: 1px solid rgba(37,164,100,0.25);
  padding: 2px 8px;
  border-radius: 20px;
  flex-shrink: 0;
}
.skill-desc {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: auto;
}
.skill-tags { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.clickable-tag { cursor: pointer; transition: all 0.15s; }
.clickable-tag:hover { background: var(--accent); color: #fff; border-color: var(--accent); transform: translateY(-1px); }
.stat { font-size: 0.78rem; color: var(--text-muted); }
</style>
