<template>
  <div id="layout">
    <AppHeader />
    <main>
      <RouterView />
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
</script>

<style scoped>
#layout { display: flex; flex-direction: column; min-height: 100vh; }
main { flex: 1; }
</style>
