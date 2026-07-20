<template>
  <AdminLayout activeRoute="dashboard">
    <div class="dashboard">
      <h2 class="page-title">仪表盘</h2>

      <div class="stat-grid">
        <StatCard label="总考生数" :value="data.total_users" color="blue" />
        <StatCard label="总通过率" :value="data.overall_pass_rate + '%'" color="green" />
        <StatCard label="题目数" :value="data.total_articles" color="amber" />
      </div>

      <div class="card">
        <h3 class="card-title">各题目通过率</h3>
        <div class="bar-list">
          <div v-for="a in data.article_stats" :key="a.filename" class="bar-item">
            <div class="bar-header">
              <span class="bar-label">{{ a.title }}</span>
              <span class="bar-value">{{ a.pass_rate }}% ({{ a.passed }}/{{ a.attempted }})</span>
            </div>
            <div class="bar-track">
              <div class="bar-fill" :style="{ width: a.pass_rate + '%' }"></div>
            </div>
          </div>
          <div v-if="!data.article_stats?.length" class="empty">暂无数据</div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminLayout from './components/AdminLayout.vue'
import StatCard from './components/StatCard.vue'

const API_BASE = 'http://localhost:8000'
const data = ref({ total_users: 0, overall_pass_rate: 0, total_articles: 0, article_stats: [] })

const getHeaders = () => {
  const t = localStorage.getItem('admin_token')
  return t ? { Authorization: `Bearer ${t}` } : {}
}

onMounted(async () => {
  try {
    const res = await fetch(`${API_BASE}/admin/dashboard`, { headers: getHeaders() })
    if (res.ok) data.value = await res.json()
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
.dashboard { }
.page-title { font-size: 22px; font-weight: 700; color: #0f172a; margin-bottom: 24px; }
.stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 28px; }
.card { background: #fff; border-radius: 10px; padding: 24px; border: 1px solid #e2e8f0; }
.card-title { font-size: 15px; font-weight: 600; color: #0f172a; margin-bottom: 18px; }
.bar-list { display: flex; flex-direction: column; gap: 16px; }
.bar-header { display: flex; justify-content: space-between; margin-bottom: 6px; }
.bar-label { font-size: 13px; color: #475569; font-weight: 500; }
.bar-value { font-size: 12px; color: #64748b; }
.bar-track { height: 8px; background: #e2e8f0; border-radius: 4px; }
.bar-fill { height: 8px; background: linear-gradient(90deg, #4a6cf7, #6a3de8); border-radius: 4px; transition: width 0.6s ease; }
.empty { color: #94a3b8; font-size: 13px; text-align: center; padding: 20px 0; }
</style>
