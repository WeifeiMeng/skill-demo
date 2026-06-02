<template>
  <div class="student-list">
    <h2 class="page-title">考生数据</h2>

    <div class="stat-grid">
      <StatCard label="总考生" :value="data.total_students" color="#4a6cf7" />
      <StatCard label="已通过" :value="data.passed_students" color="#22c55e" />
      <StatCard label="未通过" :value="data.failed_students" color="#ef4444" />
    </div>

    <div class="card">
      <table class="table" v-if="data.students?.length">
        <thead>
          <tr>
            <th>姓名</th><th>邮箱</th><th>完成题数</th><th>通过率</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in data.students" :key="s.id">
            <td class="td-name">{{ s.name }}</td>
            <td class="td-email">{{ s.email }}</td>
            <td class="td-center">{{ s.completed }}/{{ s.total }}</td>
            <td class="td-center">
              <span :class="s.pass_rate >= 50 ? 'rate-pass' : 'rate-fail'">{{ s.pass_rate }}%</span>
            </td>
            <td class="td-center">
              <router-link :to="`/students/${s.id}`" class="btn-detail">详情</router-link>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty">暂无考生数据</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import StatCard from '../components/StatCard.vue'

const API_BASE = 'http://localhost:8000'
const data = ref({ total_students: 0, passed_students: 0, failed_students: 0, students: [] })

const getHeaders = () => {
  const t = localStorage.getItem('admin_token')
  return t ? { Authorization: `Bearer ${t}` } : {}
}

onMounted(async () => {
  const res = await fetch(`${API_BASE}/admin/students`, { headers: getHeaders() })
  if (res.ok) data.value = await res.json()
})
</script>

<style scoped>
.student-list { max-width: 960px; }
.page-title { font-size: 22px; font-weight: 700; color: #0f172a; margin-bottom: 24px; }
.stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 28px; }
.card { background: #fff; border-radius: 10px; border: 1px solid #e2e8f0; overflow: hidden; }
.table { width: 100%; border-collapse: collapse; font-size: 13px; }
.table th { text-align: left; padding: 12px 16px; background: #f8fafc; color: #64748b; font-weight: 600; font-size: 12px; text-transform: uppercase; }
.table td { padding: 12px 16px; border-top: 1px solid #f1f5f9; color: #334155; }
.td-name { font-weight: 500; }
.td-email { color: #64748b; }
.td-center { text-align: center; }
.rate-pass { color: #16a34a; font-weight: 600; }
.rate-fail { color: #dc2626; font-weight: 600; }
.btn-detail { color: #4a6cf7; font-weight: 500; font-size: 12px; }
.empty { color: #94a3b8; font-size: 13px; text-align: center; padding: 32px 0; }
</style>
