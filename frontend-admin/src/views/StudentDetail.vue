<template>
  <div class="student-detail">
    <div class="page-header">
      <router-link to="/students" class="back-link">← 返回列表</router-link>
      <h2 class="page-title">{{ data.name }}</h2>
      <span class="page-email">{{ data.email }}</span>
    </div>

    <div class="stat-grid">
      <div class="sum-card"><div class="sum-label">完成题目</div><div class="sum-value">{{ data.completed }}/{{ data.total }}</div></div>
      <div class="sum-card"><div class="sum-label">总通过率</div><div class="sum-value rate-pass">{{ data.pass_rate }}%</div></div>
      <div class="sum-card"><div class="sum-label">平均得分</div><div class="sum-value">{{ data.avg_score }}</div></div>
    </div>

    <div class="card">
      <h3 class="card-title">答题记录</h3>
      <div v-if="data.article_records?.length">
        <div v-for="r in data.article_records" :key="r.article_name" class="record-item">
          <div class="record-header" @click="toggle(r.article_name)">
            <div class="record-info">
              <span class="record-title">{{ r.article_title }}</span>
              <span class="record-count">{{ r.submission_count }} 次提交</span>
            </div>
            <div class="record-result">
              <span v-if="r.passed === null" class="status-none">未开始</span>
              <span v-else :class="r.passed ? 'status-pass' : 'status-fail'">
                {{ r.latest_score }}分 {{ r.passed ? 'PASS' : 'FAIL' }}
              </span>
              <button
                class="reset-btn"
                :disabled="resetting[r.article_name]"
                @click.stop="resetSession(r.article_name)"
              >{{ resetting[r.article_name] ? '重置中...' : '重置时间' }}</button>
              <span class="toggle-arrow">{{ expanded[r.article_name] ? '▾' : '▸' }}</span>
            </div>
          </div>
          <div v-if="expanded[r.article_name] && r.cases?.length" class="record-cases">
            <div v-for="(c, i) in r.cases" :key="i" class="case-row" :class="c.passed ? 'case-pass' : 'case-fail'">
              <span>{{ c.passed ? '✓' : '✗' }} {{ c.name }}</span>
              <span v-if="c.score !== undefined" class="case-score">{{ c.score }}分</span>
              <span v-if="c.message" class="case-msg">{{ c.message }}</span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty">暂无答题记录</div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const API_BASE = 'http://localhost:8000'
const data = ref({ name: '', email: '', completed: 0, total: 0, pass_rate: 0, avg_score: 0, article_records: [] })
const expanded = reactive({})
const resetting = reactive({})

const getHeaders = () => {
  const t = localStorage.getItem('admin_token')
  return t ? { Authorization: `Bearer ${t}` } : {}
}

const toggle = (name) => { expanded[name] = !expanded[name] }

const resetSession = async (articleName) => {
  resetting[articleName] = true
  try {
    const res = await fetch(
      `${API_BASE}/admin/students/${route.params.id}/articles/${articleName}/reset-session`,
      { method: 'POST', headers: { ...getHeaders(), 'Content-Type': 'application/json' } }
    )
    if (res.ok) {
      alert('会话已重置，考生可重新进入')
    } else {
      const err = await res.json().catch(() => ({}))
      alert(err.detail || '重置失败')
    }
  } catch (e) {
    alert('重置请求失败: ' + e.message)
  } finally {
    resetting[articleName] = false
  }
}

onMounted(async () => {
  const res = await fetch(`${API_BASE}/admin/students/${route.params.id}`, { headers: getHeaders() })
  if (res.ok) data.value = await res.json()
})
</script>

<style scoped>
.student-detail { max-width: 960px; }
.page-header { margin-bottom: 24px; }
.back-link { color: #64748b; font-size: 13px; display: inline-block; margin-bottom: 8px; }
.back-link:hover { color: #4a6cf7; }
.page-title { font-size: 22px; font-weight: 700; color: #0f172a; display: inline; margin-right: 12px; }
.page-email { color: #64748b; font-size: 14px; }
.stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 28px; }
.sum-card { background: #fff; border-radius: 8px; padding: 16px; text-align: center; border: 1px solid #e2e8f0; }
.sum-label { font-size: 12px; color: #94a3b8; }
.sum-value { font-size: 24px; font-weight: 700; color: #0f172a; margin-top: 4px; }
.rate-pass { color: #22c55e; }
.card { background: #fff; border-radius: 10px; border: 1px solid #e2e8f0; padding: 24px; }
.card-title { font-size: 15px; font-weight: 600; color: #0f172a; margin-bottom: 16px; }
.record-item { border-bottom: 1px solid #f1f5f9; }
.record-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 0; cursor: pointer;
}
.record-info { display: flex; gap: 10px; align-items: baseline; }
.record-title { font-size: 14px; font-weight: 500; color: #334155; }
.record-count { font-size: 12px; color: #94a3b8; }
.record-result { display: flex; align-items: center; gap: 12px; }
.status-pass { color: #16a34a; font-weight: 600; font-size: 13px; }
.status-fail { color: #dc2626; font-weight: 600; font-size: 13px; }
.status-none { color: #94a3b8; font-size: 13px; }
.toggle-arrow { color: #94a3b8; font-size: 16px; }
.record-cases { padding: 0 0 14px 14px; }
.case-row {
  display: flex; gap: 12px; align-items: center;
  padding: 8px 12px; border-radius: 6px; font-size: 13px; margin-bottom: 4px;
}
.case-pass { background: #f0fdf4; }
.case-fail { background: #fef2f2; }
.case-score { color: #64748b; font-size: 12px; margin-left: auto; }
.case-msg { color: #94a3b8; font-size: 12px; }
.reset-btn {
  background: #fef3c7; color: #b45309; border: 1px solid #f59e0b;
  padding: 3px 10px; border-radius: 6px; font-size: 12px; cursor: pointer;
  white-space: nowrap;
}
.reset-btn:hover { background: #fde68a; }
.reset-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.empty { color: #94a3b8; font-size: 13px; text-align: center; padding: 24px 0; }
</style>
