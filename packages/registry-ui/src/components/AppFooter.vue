<template>
  <footer class="app-footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <span>🧠 <strong>AgentSkills Registry</strong></span>
        <span class="footer-desc">開源的 AI Agent Skills 登錄平台</span>
      </div>
      <div class="footer-links">
        <a href="https://github.com/agentskills/registry" target="_blank">GitHub</a>
        <RouterLink to="/publish">發布 Skill</RouterLink>
        <RouterLink to="/skills">瀏覽 Skills</RouterLink>
      </div>
      <p class="footer-copy">MIT License · Built with ❤️ for the AI Agent community</p>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  border-top: 1px solid var(--border-subtle);
  margin-top: 4rem;
  padding: 2.5rem 1.5rem;
}
.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  text-align: center;
}
.footer-brand { display: flex; flex-direction: column; gap: 0.25rem; }
.footer-desc { color: var(--text-muted); font-size: 0.85rem; }
.footer-links { display: flex; gap: 1.5rem; }
.footer-links a { color: var(--text-secondary); font-size: 0.88rem; transition: color 0.15s; }
.footer-links a:hover { color: var(--accent); }
.footer-copy { color: var(--text-muted); font-size: 0.78rem; }
</style>
