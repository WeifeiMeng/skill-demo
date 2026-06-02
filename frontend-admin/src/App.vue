<template>
  <div class="admin-layout" v-if="showSidebar">
    <Sidebar />
    <main class="admin-main">
      <router-view />
    </main>
  </div>
  <router-view v-else />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './components/Sidebar.vue'

const route = useRoute()
const showSidebar = computed(() => route.name !== 'login')
</script>

<style scoped>
.admin-layout { display: flex; min-height: 100vh; }
.admin-main { flex: 1; padding: 32px; overflow-y: auto; }
</style>
