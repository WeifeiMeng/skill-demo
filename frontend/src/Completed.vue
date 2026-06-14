<template>
  <div class="completed-page">
    <div class="completed-card">
      <div class="done-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M8 12l3 3 5-5"/>
        </svg>
      </div>
      <h1 class="completed-title">您已完成考试</h1>
      <p class="completed-sub" v-if="articleTitle">{{ articleTitle }}</p>
      <p class="completed-status">状态：<span class="status-text">已完成</span></p>
      <button class="back-home-btn" @click="$router.push({ name: 'challenges' })">返回首页</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const articleTitle = ref('')

const API_BASE = 'http://localhost:8000'
const getHeaders = () => {
  const t = localStorage.getItem('token')
  return t ? { 'Authorization': `Bearer ${t}` } : {}
}

onMounted(async () => {
  try {
    const filename = route.params.filename
    const res = await fetch(`${API_BASE}/articles`)
    if (res.ok) {
      const articles = await res.json()
      const found = articles.find(a => a.filename === filename)
      if (found) articleTitle.value = found.title
    }
  } catch (_) {}
})
</script>

<style scoped>
.completed-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
}

.completed-card {
  text-align: center;
  padding: 48px 40px;
  max-width: 400px;
  width: 100%;
}

.done-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 24px;
  color: #22c55e;
}

.done-icon svg {
  width: 100%;
  height: 100%;
}

.completed-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px;
}

.completed-sub {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 16px;
}

.completed-status {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 32px;
}

.status-text {
  color: #22c55e;
  font-weight: 600;
}

.back-home-btn {
  padding: 10px 32px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}
.back-home-btn:hover {
  opacity: 0.9;
}
</style>
