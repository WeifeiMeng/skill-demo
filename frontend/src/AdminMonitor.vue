<template>
  <AdminLayout activeRoute="monitor">
    <div class="monitor-page">
      <!-- No exam ID -->
      <div v-if="!examId" class="monitor-page__no-exam">
        <p>请从考试管理页面选择一个进行中的考试进行监控。</p>
        <router-link to="/admin/exams" class="monitor-page__back-link">前往考试管理</router-link>
      </div>

      <template v-else>
        <!-- Top Info Bar -->
        <div class="monitor-page__top-bar">
          <div class="monitor-page__top-left">
            <h2 class="monitor-page__exam-name">{{ data.examName }}</h2>
            <StatusBadge
              v-if="data.status"
              :label="data.status === 'active' ? '进行中' : data.status"
              :variant="data.status === 'active' ? 'active' : 'default'"
            />
            <span
              class="monitor-page__pulse-dot"
              :class="{ 'monitor-page__pulse-dot--active': data.status === 'active' }"
            ></span>
          </div>
          <div class="monitor-page__top-center">
            <span class="monitor-page__online-count">
              在线人数: <strong>{{ data.onlineCount }}</strong>
            </span>
          </div>
          <div class="monitor-page__top-right">
            <span class="monitor-page__countdown-label">剩余时间</span>
            <span class="monitor-page__countdown-value">{{ countdownDisplay }}</span>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="monitor-page__loading">
          <div class="monitor-page__loading-spinner"></div>
          <span>加载监控数据...</span>
        </div>

        <!-- Three Column Layout -->
        <div v-else class="monitor-page__grid">
          <!-- Left Column: Stats -->
          <div class="monitor-page__left">
            <div class="monitor-page__card">
              <h4 class="monitor-page__card-title">考试统计</h4>
              <div class="monitor-page__stat-list">
                <div class="monitor-page__stat-row">
                  <span class="monitor-page__stat-label">总人数</span>
                  <span class="monitor-page__stat-value">{{ statsData.total }}</span>
                </div>
                <div class="monitor-page__stat-row">
                  <span class="monitor-page__stat-label">在线</span>
                  <span class="monitor-page__stat-value monitor-page__stat-value--online">
                    <span class="monitor-page__stat-dot monitor-page__stat-dot--green"></span>
                    {{ statsData.online }}
                  </span>
                </div>
                <div class="monitor-page__stat-row">
                  <span class="monitor-page__stat-label">离线</span>
                  <span class="monitor-page__stat-value monitor-page__stat-value--offline">{{ statsData.offline }}</span>
                </div>
                <div class="monitor-page__stat-row">
                  <span class="monitor-page__stat-label">已提交</span>
                  <span class="monitor-page__stat-value monitor-page__stat-value--submitted">{{ statsData.submitted }}</span>
                </div>
                <div class="monitor-page__stat-row">
                  <span class="monitor-page__stat-label">告警</span>
                  <span
                    class="monitor-page__stat-value monitor-page__stat-value--alert"
                    :class="{ 'monitor-page__stat-value--pulse': statsData.alerts > 0 }"
                  >
                    {{ statsData.alerts }}
                  </span>
                </div>
              </div>
            </div>

            <div class="monitor-page__card">
              <h4 class="monitor-page__card-title">各题进度</h4>
              <div class="monitor-page__question-list">
                <div
                  v-for="q in questionProgress"
                  :key="q.name"
                  class="monitor-page__question-item"
                >
                  <div class="monitor-page__question-header">
                    <span class="monitor-page__question-name">{{ q.name }}</span>
                    <span class="monitor-page__question-count">{{ q.completed }}/{{ q.total }}</span>
                  </div>
                  <div class="monitor-page__question-bar">
                    <div
                      class="monitor-page__question-fill"
                      :style="{ width: q.total > 0 ? (q.completed / q.total * 100) + '%' : '0%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <div class="monitor-page__card">
              <h4 class="monitor-page__card-title">容器资源</h4>
              <div class="monitor-page__resource-list">
                <div v-for="c in resourceContainers" :key="c.name" class="monitor-page__resource-row">
                  <span
                    class="monitor-page__resource-dot"
                    :class="{
                      'monitor-page__resource-dot--green': c.cpuLevel === 'green',
                      'monitor-page__resource-dot--amber': c.cpuLevel === 'amber',
                      'monitor-page__resource-dot--red': c.cpuLevel === 'red',
                    }"
                  ></span>
                  <span class="monitor-page__resource-name">{{ c.name }}</span>
                  <span class="monitor-page__resource-meta">
                    CPU {{ c.cpu }}% | 内存 {{ c.mem }}MB
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Center Column: Candidates -->
          <div class="monitor-page__center">
            <div class="monitor-page__candidate-grid">
              <div
                v-for="c in candidates"
                :key="c.id || c.name"
                class="monitor-page__candidate-card"
                :class="{ 'monitor-page__candidate-card--alert': c.hasAlert }"
              >
                <div class="monitor-page__candidate-top">
                  <div
                    class="monitor-page__candidate-avatar"
                    :style="{ backgroundColor: avatarColor(c.name) }"
                  >
                    {{ c.name.charAt(0) }}
                  </div>
                  <div class="monitor-page__candidate-info">
                    <span class="monitor-page__candidate-name">{{ c.name }}</span>
                    <span
                      class="monitor-page__candidate-status"
                      :class="{
                        'monitor-page__candidate-status--online': c.status === 'online',
                        'monitor-page__candidate-status--idle': c.status === 'offline',
                        'monitor-page__candidate-status--alert': c.hasAlert,
                      }"
                    ></span>
                  </div>
                </div>
                <div class="monitor-page__candidate-question">{{ c.currentQuestion || '-' }}</div>
                <div class="monitor-page__candidate-progress-bar">
                  <div
                    class="monitor-page__candidate-progress-fill"
                    :style="{ width: (c.progress || 0) + '%' }"
                  ></div>
                </div>
                <div class="monitor-page__candidate-bottom">
                  <span>{{ c.duration }}</span>
                  <span>提交 {{ c.submissionCount }} 次</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Column: Alerts -->
          <div class="monitor-page__right">
            <div class="monitor-page__card">
              <div class="monitor-page__alert-header">
                <span class="monitor-page__alert-dot"></span>
                <h4 class="monitor-page__card-title">实时告警</h4>
              </div>
              <div class="monitor-page__alert-list">
                <div
                  v-for="(alert, idx) in alerts"
                  :key="idx"
                  class="monitor-page__alert-item"
                >
                  <span class="monitor-page__alert-time">{{ alert.time }}</span>
                  <span class="monitor-page__alert-text">{{ alert.text }}</span>
                  <button class="monitor-page__alert-action">查看详情</button>
                  <div v-if="idx < alerts.length - 1" class="monitor-page__alert-sep"></div>
                </div>
                <div v-if="alerts.length === 0" class="monitor-page__alert-empty">
                  暂无告警
                </div>
              </div>
            </div>

            <div class="monitor-page__card">
              <h4 class="monitor-page__card-title">快捷操作</h4>
              <div class="monitor-page__quick-actions">
                <button class="monitor-page__quick-btn">全体广播</button>
                <button class="monitor-page__quick-btn">延长考试</button>
                <button class="monitor-page__quick-btn">导出数据</button>
                <button class="monitor-page__quick-btn">审计日志</button>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import AdminLayout from './components/AdminLayout.vue'
import StatusBadge from './components/StatusBadge.vue'
import { fetchMonitorData } from './data/api.js'

const route = useRoute()
const examId = computed(() => route.params.examId)

const loading = ref(true)
const data = reactive({
  examName: '',
  status: 'active',
  onlineCount: 0,
  remainingTime: '',
})

const statsData = reactive({ total: 0, online: 0, offline: 0, submitted: 0, alerts: 0 })
const questionProgress = ref([])
const resourceContainers = ref([])
const candidates = ref([])
const alerts = ref([])

let countdownSeconds = 0
let countdownTimer = null
let refreshTimer = null

const countdownDisplay = ref('--:--:--')

function parseTimerToSeconds(timer) {
  if (!timer) return 0
  const parts = timer.split(':').map(Number)
  if (parts.length === 3) {
    return parts[0] * 3600 + parts[1] * 60 + parts[2]
  }
  return 0
}

function formatSeconds(total) {
  if (total <= 0) return '00:00:00'
  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = total % 60
  return [h, m, s].map((v) => String(v).padStart(2, '0')).join(':')
}

function startCountdown(initial) {
  countdownSeconds = typeof initial === 'number' ? initial : parseTimerToSeconds(initial)
  countdownDisplay.value = formatSeconds(countdownSeconds)
  clearInterval(countdownTimer)
  countdownTimer = setInterval(() => {
    if (countdownSeconds > 0) {
      countdownSeconds--
      countdownDisplay.value = formatSeconds(countdownSeconds)
    } else {
      clearInterval(countdownTimer)
    }
  }, 1000)
}

function avatarColor(name) {
  const colors = ['#4a6cf7', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316']
  let hash = 0
  for (let i = 0; i < (name || '').length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

function getCpuLevel(cpu) {
  if (cpu < 60) return 'green'
  if (cpu < 85) return 'amber'
  return 'red'
}

async function refreshData() {
  try {
    const id = examId.value
    if (!id) return
    const result = await fetchMonitorData(id)

    // Normalize data from mock shapes
    data.examName = result.title || result.examName || ''
    data.status = result.status || 'active'
    data.onlineCount = result.onlineCount ?? result.online ?? 0
    data.remainingTime = result.timer || result.remainingTime || ''

    // Stats
    if (result.stats) {
      statsData.total = result.stats.total ?? 0
      statsData.online = result.stats.online ?? 0
      statsData.offline = result.stats.offline ?? 0
      statsData.submitted = result.stats.submitted ?? 0
      statsData.alerts = result.stats.alerts ?? 0
    } else {
      statsData.total = (result.online || 0) + (result.offline || 0) + (result.submitted || 0)
      statsData.online = result.online || 0
      statsData.offline = result.offline || 0
      statsData.submitted = result.submitted || 0
      statsData.alerts = result.alerts || 0
    }

    // Question progress - normalize from mock
    questionProgress.value = (result.questionProgress || []).map((q) => ({
      name: q.name,
      completed: q.completed ?? Math.round((q.progress || 0) / 100 * 4),
      total: q.total ?? 4,
    }))

    // Resources - normalize from mock
    const containers = result.resourceStatus?.containers || result.containers || []
    resourceContainers.value = containers.map((c) => ({
      name: c.name,
      cpu: c.cpu || 0,
      mem: c.mem || c.memory || 0,
      cpuLevel: getCpuLevel(c.cpu || 0),
    }))

    // Candidates - normalize from mock
    candidates.value = (result.candidates || []).map((c) => ({
      id: c.id || c.name,
      name: c.name,
      avatar: c.avatar || '',
      status: c.status,
      currentQuestion: c.currentQuestion || c.question || '',
      progress: c.progress ?? c.completed ?? 0,
      duration: c.duration || c.timeUsed || '',
      submissionCount: c.submissionCount ?? c.submits ?? 0,
      hasAlert: c.hasAlert ?? c.alert ?? false,
    }))

    // Alerts - normalize from mock
    const rawAlerts = result.alerts || result.alertLog || []
    alerts.value = rawAlerts.map((a) => ({
      time: a.time,
      text: a.text,
      candidateId: a.candidateId || '',
    }))

    // Countdown
    if (data.remainingTime && loading.value) {
      startCountdown(data.remainingTime)
    }
  } catch (e) {
    console.error('Failed to load monitor data:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshData()
  refreshTimer = setInterval(refreshData, 10000)
})

onUnmounted(() => {
  clearInterval(countdownTimer)
  clearInterval(refreshTimer)
})
</script>

<style scoped>
.monitor-page__no-exam {
  text-align: center;
  padding: 80px 20px;
  color: #64748b;
  font-size: 14px;
}

.monitor-page__back-link {
  display: inline-block;
  margin-top: 12px;
  color: #4a6cf7;
  font-weight: 600;
  text-decoration: none;
}

.monitor-page__back-link:hover {
  text-decoration: underline;
}

/* Top Bar */
.monitor-page__top-bar {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.monitor-page__top-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.monitor-page__exam-name {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.monitor-page__top-center {
  flex: 1;
  text-align: center;
}

.monitor-page__online-count {
  font-size: 15px;
  color: #475569;
}

.monitor-page__online-count strong {
  color: #1e293b;
  font-size: 20px;
  font-weight: 700;
}

.monitor-page__top-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.monitor-page__countdown-label {
  font-size: 11px;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.monitor-page__countdown-value {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  font-family: monospace;
}

/* Pulse Dot */
.monitor-page__pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #94a3b8;
  display: none;
}

.monitor-page__pulse-dot--active {
  display: block;
  background: #22c55e;
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.5); }
}

/* Loading */
.monitor-page__loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 80px 20px;
  color: #64748b;
  font-size: 14px;
}

.monitor-page__loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e2e8f0;
  border-top-color: #4a6cf7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Three Column Grid */
.monitor-page__grid {
  display: grid;
  grid-template-columns: 280px 1fr 300px;
  gap: 20px;
  align-items: start;
}

/* Card */
.monitor-page__card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 16px;
}

.monitor-page__card-title {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  margin: 0 0 14px;
}

/* Left Column */
.monitor-page__stat-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.monitor-page__stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.monitor-page__stat-label {
  font-size: 13px;
  color: #64748b;
}

.monitor-page__stat-value {
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 6px;
}

.monitor-page__stat-value--online {
  color: #22c55e;
}

.monitor-page__stat-value--offline {
  color: #94a3b8;
}

.monitor-page__stat-value--submitted {
  color: #22c55e;
}

.monitor-page__stat-value--alert {
  color: #ef4444;
}

.monitor-page__stat-value--pulse {
  animation: pulse-dot 1.5s ease-in-out infinite;
}

.monitor-page__stat-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  display: inline-block;
}

.monitor-page__stat-dot--green {
  background: #22c55e;
}

/* Question Progress */
.monitor-page__question-item {
  margin-bottom: 12px;
}

.monitor-page__question-item:last-child {
  margin-bottom: 0;
}

.monitor-page__question-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.monitor-page__question-name {
  font-size: 12px;
  color: #475569;
  font-weight: 500;
}

.monitor-page__question-count {
  font-size: 11px;
  color: #94a3b8;
}

.monitor-page__question-bar {
  height: 5px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.monitor-page__question-fill {
  height: 100%;
  background: #4a6cf7;
  border-radius: 3px;
  transition: width 0.5s ease;
}

/* Resource */
.monitor-page__resource-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.monitor-page__resource-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.monitor-page__resource-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.monitor-page__resource-dot--green {
  background: #22c55e;
}

.monitor-page__resource-dot--amber {
  background: #f59e0b;
}

.monitor-page__resource-dot--red {
  background: #ef4444;
  animation: pulse-dot 1.5s ease-in-out infinite;
}

.monitor-page__resource-name {
  font-size: 12px;
  color: #475569;
  font-weight: 500;
  flex-shrink: 0;
}

.monitor-page__resource-meta {
  font-size: 11px;
  color: #94a3b8;
  margin-left: auto;
}

/* Center Candidate Grid */
.monitor-page__candidate-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.monitor-page__candidate-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.monitor-page__candidate-card:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.monitor-page__candidate-card--alert {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.02);
}

.monitor-page__candidate-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.monitor-page__candidate-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.monitor-page__candidate-info {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  min-width: 0;
}

.monitor-page__candidate-name {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.monitor-page__candidate-status {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.monitor-page__candidate-status--online {
  background: #22c55e;
}

.monitor-page__candidate-status--idle {
  background: #f59e0b;
}

.monitor-page__candidate-status--alert {
  background: #ef4444;
  animation: pulse-dot 1.5s ease-in-out infinite;
}

.monitor-page__candidate-question {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.monitor-page__candidate-progress-bar {
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 8px;
}

.monitor-page__candidate-progress-fill {
  height: 100%;
  background: #4a6cf7;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.monitor-page__candidate-bottom {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #94a3b8;
}

/* Right Column */
.monitor-page__alert-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}

.monitor-page__alert-header .monitor-page__card-title {
  margin: 0;
}

.monitor-page__alert-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ef4444;
  animation: pulse-dot 1.5s ease-in-out infinite;
}

.monitor-page__alert-list {
  display: flex;
  flex-direction: column;
}

.monitor-page__alert-item {
  position: relative;
  padding: 6px 0;
}

.monitor-page__alert-time {
  font-size: 11px;
  color: #94a3b8;
  display: block;
  margin-bottom: 2px;
}

.monitor-page__alert-text {
  font-size: 13px;
  color: #334155;
  line-height: 1.5;
  display: block;
  margin-bottom: 4px;
}

.monitor-page__alert-action {
  background: none;
  border: none;
  color: #4a6cf7;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  padding: 0;
}

.monitor-page__alert-action:hover {
  text-decoration: underline;
}

.monitor-page__alert-sep {
  height: 1px;
  background: #f1f5f9;
  margin-top: 8px;
}

.monitor-page__alert-empty {
  font-size: 13px;
  color: #94a3b8;
  text-align: center;
  padding: 16px 0;
}

/* Quick Actions */
.monitor-page__quick-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.monitor-page__quick-btn {
  width: 100%;
  padding: 10px;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  background: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
}

.monitor-page__quick-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  color: #1e293b;
}
</style>
