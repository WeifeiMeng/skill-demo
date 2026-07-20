<template>
  <AdminLayout activeRoute="monitor">
    <div class="monitor-page">
      <!-- No exam ID -->
      <div v-if="!effectiveExamId && !autoDetecting" class="monitor-page__no-exam">
        <p>当前没有进行中的考试场次。</p>
        <router-link to="/admin/exams" class="monitor-page__back-link">前往考试管理</router-link>
      </div>
      <div v-else-if="autoDetecting" class="monitor-page__loading">
        <div class="monitor-page__loading-spinner"></div>
        <span>正在查找进行中的考试...</span>
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
            <!-- Candidate Filters -->
            <div class="monitor-page__candidate-filters">
              <div class="monitor-page__filter-tabs">
                <button
                  v-for="tab in candidateTabs"
                  :key="tab.key"
                  class="monitor-page__filter-tab"
                  :class="{ 'monitor-page__filter-tab--active': activeCandidateTab === tab.key }"
                  @click="activeCandidateTab = tab.key"
                >
                  {{ tab.label }}
                  <span class="monitor-page__filter-tab-count">{{ tab.count }}</span>
                </button>
              </div>
              <input
                v-model="candidateSearch"
                type="text"
                class="monitor-page__candidate-search"
                placeholder="搜索考生姓名..."
              />
            </div>
            <div class="monitor-page__candidate-grid">
              <div v-if="filteredCandidates.length === 0" class="monitor-page__candidate-empty">
                暂无匹配考生
              </div>
              <div
                v-for="c in filteredCandidates"
                :key="c.id || c.name"
                class="monitor-page__candidate-card"
                :class="{ 'monitor-page__candidate-card--alert': c.hasAlert, 'monitor-page__candidate-card--selected': selectedCandidate === c }"
                @click="selectCandidate(c)"
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

          <!-- Right Column: Activity Timeline -->
          <div class="monitor-page__right">
            <div class="monitor-page__card">
              <div class="monitor-page__alert-header">
                <span class="monitor-page__alert-dot"></span>
                <h4 class="monitor-page__card-title">实时活动</h4>
              </div>
              <div class="monitor-page__timeline">
                <div
                  v-for="(event, idx) in activityTimeline"
                  :key="idx"
                  class="monitor-page__timeline-item"
                  :class="'monitor-page__timeline-item--' + event.level"
                >
                  <div class="monitor-page__timeline-marker">
                    <span class="monitor-page__timeline-icon">{{ event.icon }}</span>
                  </div>
                  <div class="monitor-page__timeline-content">
                    <span class="monitor-page__timeline-time">{{ event.time }}</span>
                    <span class="monitor-page__timeline-text">{{ event.text }}</span>
                    <span v-if="event.candidate" class="monitor-page__timeline-candidate">
                      {{ event.candidate }}
                    </span>
                  </div>
                  <div class="monitor-page__timeline-line"></div>
                </div>
                <div v-if="activityTimeline.length === 0" class="monitor-page__alert-empty">
                  暂无活动
                </div>
              </div>
            </div>

            <div class="monitor-page__card">
              <h4 class="monitor-page__card-title">快捷操作</h4>
              <div class="monitor-page__quick-actions">
                <button class="monitor-page__quick-btn" @click="broadcastMessage">📢 全体广播</button>
                <button class="monitor-page__quick-btn" @click="extendExam">⏱️ 延长考试</button>
                <button class="monitor-page__quick-btn" @click="exportData">📥 导出数据</button>
                <button class="monitor-page__quick-btn" @click="viewAuditLog">📋 审计日志</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Candidate Detail Slide-out Panel -->
        <div v-if="selectedCandidate" class="monitor-page__panel-overlay" @click.self="selectedCandidate = null">
          <div class="monitor-page__detail-panel">
            <div class="monitor-page__detail-panel-header">
              <div class="monitor-page__detail-panel-user">
                <div
                  class="monitor-page__detail-panel-avatar"
                  :style="{ backgroundColor: avatarColor(selectedCandidate.name) }"
                >
                  {{ selectedCandidate.name.charAt(0) }}
                </div>
                <div>
                  <h3 class="monitor-page__detail-panel-name">{{ selectedCandidate.name }}</h3>
                  <span
                    class="monitor-page__detail-panel-status"
                    :class="{
                      'monitor-page__candidate-status--online': selectedCandidate.status === 'online',
                      'monitor-page__candidate-status--idle': selectedCandidate.status === 'offline',
                      'monitor-page__candidate-status--alert': selectedCandidate.hasAlert,
                    }"
                  ></span>
                  <span class="monitor-page__detail-panel-status-text">
                    {{ selectedCandidate.status === 'online' ? '在线' : '离线' }}
                    <template v-if="selectedCandidate.hasAlert"> · 告警</template>
                  </span>
                </div>
              </div>
              <button class="monitor-page__detail-panel-close" @click="selectedCandidate = null">&times;</button>
            </div>

            <!-- AI Risk Score -->
            <div class="monitor-page__detail-section">
              <h5 class="monitor-page__detail-section-title">AI 风险评分</h5>
              <div class="monitor-page__risk-bar-wrapper">
                <div class="monitor-page__risk-bar">
                  <div
                    class="monitor-page__risk-bar-fill"
                    :class="{
                      'monitor-page__risk-bar-fill--low': candidateDetail.riskScore <= 30,
                      'monitor-page__risk-bar-fill--mid': candidateDetail.riskScore > 30 && candidateDetail.riskScore <= 60,
                      'monitor-page__risk-bar-fill--high': candidateDetail.riskScore > 60,
                    }"
                    :style="{ width: candidateDetail.riskScore + '%' }"
                  ></div>
                </div>
                <span
                  class="monitor-page__risk-score"
                  :class="{
                    'monitor-page__risk-score--low': candidateDetail.riskScore <= 30,
                    'monitor-page__risk-score--mid': candidateDetail.riskScore > 30 && candidateDetail.riskScore <= 60,
                    'monitor-page__risk-score--high': candidateDetail.riskScore > 60,
                  }"
                >
                  {{ candidateDetail.riskScore }} / 100
                </span>
              </div>
              <div class="monitor-page__risk-factors">
                <div class="monitor-page__risk-factor">
                  <span class="monitor-page__risk-factor-label">切屏次数</span>
                  <span class="monitor-page__risk-factor-value">{{ candidateDetail.screenSwitches }}</span>
                </div>
                <div class="monitor-page__risk-factor">
                  <span class="monitor-page__risk-factor-label">提交频率</span>
                  <span class="monitor-page__risk-factor-value">{{ candidateDetail.submitFrequency }}</span>
                </div>
                <div class="monitor-page__risk-factor">
                  <span class="monitor-page__risk-factor-label">键盘模式</span>
                  <span class="monitor-page__risk-factor-value">{{ candidateDetail.keystrokePattern }}</span>
                </div>
              </div>
            </div>

            <!-- Exam Progress -->
            <div class="monitor-page__detail-section">
              <h5 class="monitor-page__detail-section-title">考试进度</h5>
              <div class="monitor-page__detail-progress">
                <span class="monitor-page__detail-progress-label">当前题目</span>
                <span class="monitor-page__detail-progress-value">{{ selectedCandidate.currentQuestion || '-' }}</span>
              </div>
              <div class="monitor-page__detail-progress-bar">
                <div
                  class="monitor-page__detail-progress-fill"
                  :style="{ width: (selectedCandidate.progress || 0) + '%' }"
                ></div>
              </div>
              <div class="monitor-page__detail-progress-meta">
                <span>已完成 {{ selectedCandidate.progress || 0 }}%</span>
                <span>用时 {{ selectedCandidate.duration }}</span>
                <span>提交 {{ selectedCandidate.submissionCount }} 次</span>
              </div>
            </div>

            <!-- Behavior Log -->
            <div class="monitor-page__detail-section">
              <h5 class="monitor-page__detail-section-title">行为日志</h5>
              <div class="monitor-page__behavior-list">
                <div
                  v-for="(log, idx) in candidateDetail.behaviorLog"
                  :key="idx"
                  class="monitor-page__behavior-item"
                >
                  <span class="monitor-page__behavior-icon">{{ log.icon }}</span>
                  <span class="monitor-page__behavior-time">{{ log.time }}</span>
                  <span class="monitor-page__behavior-text">{{ log.text }}</span>
                </div>
                <div v-if="candidateDetail.behaviorLog.length === 0" class="monitor-page__behavior-empty">
                  暂无行为记录
                </div>
              </div>
            </div>

            <!-- Submission History -->
            <div class="monitor-page__detail-section">
              <h5 class="monitor-page__detail-section-title">提交记录</h5>
              <div class="monitor-page__submission-list">
                <div
                  v-for="(sub, idx) in candidateDetail.submissions"
                  :key="idx"
                  class="monitor-page__submission-item"
                >
                  <span class="monitor-page__submission-time">{{ sub.time }}</span>
                  <span class="monitor-page__submission-question">{{ sub.question }}</span>
                  <span
                    class="monitor-page__submission-result"
                    :class="{
                      'monitor-page__submission-result--pass': sub.result === 'PASS',
                      'monitor-page__submission-result--fail': sub.result === 'FAIL',
                    }"
                  >
                    {{ sub.result }}
                  </span>
                  <span class="monitor-page__submission-score">{{ sub.score }} 分</span>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="monitor-page__detail-actions">
              <button class="monitor-page__detail-action monitor-page__detail-action--warn" @click="warnCandidate">
                发送警告
              </button>
              <button class="monitor-page__detail-action monitor-page__detail-action--submit" @click="forceSubmit">
                强制交卷
              </button>
              <button
                v-if="selectedCandidate.status === 'offline'"
                class="monitor-page__detail-action monitor-page__detail-action--resume"
                @click="resumeCandidate"
              >
                恢复考试
              </button>
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
import { fetchMonitorData, fetchExamSessions } from './data/api.js'

const route = useRoute()
const routeExamId = computed(() => route.params.examId)
const detectedExamId = ref(null)
const autoDetecting = ref(false)
const effectiveExamId = computed(() => routeExamId.value || detectedExamId.value)

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
const activeCandidateTab = ref('all')
const candidateSearch = ref('')
const selectedCandidate = ref(null)

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

// --- Candidate Filtering ---
const candidateTabs = computed(() => {
  const list = candidates.value
  return [
    { key: 'all', label: '全部', count: list.length },
    { key: 'online', label: '在线', count: list.filter(c => c.status === 'online').length },
    { key: 'offline', label: '离线', count: list.filter(c => c.status === 'offline').length },
    { key: 'submitted', label: '已提交', count: list.filter(c => c.progress >= 100).length },
    { key: 'alert', label: '告警', count: list.filter(c => c.hasAlert).length },
  ]
})

const filteredCandidates = computed(() => {
  let result = candidates.value
  if (activeCandidateTab.value === 'online') {
    result = result.filter(c => c.status === 'online')
  } else if (activeCandidateTab.value === 'offline') {
    result = result.filter(c => c.status === 'offline')
  } else if (activeCandidateTab.value === 'submitted') {
    result = result.filter(c => c.progress >= 100)
  } else if (activeCandidateTab.value === 'alert') {
    result = result.filter(c => c.hasAlert)
  }
  if (candidateSearch.value.trim()) {
    const q = candidateSearch.value.trim().toLowerCase()
    result = result.filter(c => c.name.toLowerCase().includes(q))
  }
  return result
})

// --- Activity Timeline ---
const activityTimeline = computed(() => {
  const events = (alerts.value || []).map(a => {
    const level = a.text.includes('切屏') ? 'warning' : a.text.includes('异常') ? 'warning' : 'info'
    const icon = level === 'warning' ? '⚠️' : 'ℹ️'
    return { time: a.time, text: a.text, candidate: a.candidateId || '', level, icon }
  })
  return events
})

// --- Candidate Detail ---
function generateCandidateDetail(candidate) {
  if (!candidate) return null
  const seed = (candidate.name || '').charCodeAt(0) || 65
  const mod = (v, m) => v % m

  const riskScore = candidate.hasAlert ? 55 + mod(seed, 40) : 5 + mod(seed, 25)
  const screenSwitches = candidate.hasAlert ? 3 + mod(seed, 8) : mod(seed, 3)
  const submitFrequency = candidate.submissionCount > 5 ? '偏高' : '正常'
  const keystrokePatterns = ['稳定', '规律', '间歇', '流畅']
  const keystrokePattern = candidate.hasAlert ? '不规律' : keystrokePatterns[mod(seed, keystrokePatterns.length)]

  const behaviorLog = []
  const names = [candidate.name]
  const startTime = new Date()
  startTime.setHours(9, 0, 0)

  if (candidate.hasAlert) {
    behaviorLog.push({ icon: '🖥️', time: '10:45:22', text: '检测到切屏行为（第 3 次）' })
  }
  if (candidate.submissionCount > 5) {
    behaviorLog.push({ icon: '📤', time: '10:38:15', text: `提交频率异常（${candidate.submissionCount} 次提交）` })
  }
  behaviorLog.push({ icon: '▶️', time: '09:02:10', text: '开始考试' })
  behaviorLog.push({ icon: '👀', time: '09:05:30', text: `开始答题: ${candidate.currentQuestion || '未知题目'}` })
  if (candidate.status === 'offline') {
    behaviorLog.push({ icon: '🔌', time: '10:12:45', text: '连接断开，进入离线状态' })
  }
  behaviorLog.push({ icon: '📤', time: '09:45:00', text: `第 1 次提交` })

  // Submissions
  const questions = ['LRU 缓存设计', '二叉树遍历优化', '图最短路径算法', '动态规划综合题']
  const submissions = []
  for (let i = 0; i < Math.min(candidate.submissionCount, 8); i++) {
    const h = 9 + Math.floor(i / 2)
    const m = 15 + (i * 23) % 45
    const time = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String((i * 17) % 60).padStart(2, '0')}`
    const passed = mod(seed + i, 5) !== 0
    submissions.push({
      time,
      question: questions[mod(i, questions.length)],
      result: passed ? 'PASS' : 'FAIL',
      score: passed ? 60 + mod(seed + i, 40) : 10 + mod(seed + i, 50),
    })
  }

  return { riskScore, screenSwitches, submitFrequency, keystrokePattern, behaviorLog, submissions }
}

const candidateDetail = computed(() => {
  return generateCandidateDetail(selectedCandidate.value) || {
    riskScore: 0, screenSwitches: 0, submitFrequency: '-', keystrokePattern: '-',
    behaviorLog: [], submissions: [],
  }
})

// --- Actions ---
function selectCandidate(candidate) {
  selectedCandidate.value = candidate
}

function broadcastMessage() {
  alert('广播消息功能：可向所有在线考生发送统一通知。')
}

function extendExam() {
  const minutes = prompt('延长考试时长（分钟）：', '15')
  if (minutes) {
    countdownSeconds += parseInt(minutes) * 60
    countdownDisplay.value = formatSeconds(countdownSeconds)
    alert(`考试已延长 ${minutes} 分钟。`)
  }
}

function exportData() {
  alert('导出数据功能：将当前监控数据导出为 CSV 文件。')
}

function viewAuditLog() {
  alert('审计日志功能：查看完整操作审计记录。')
}

function warnCandidate() {
  if (selectedCandidate.value) {
    alert(`已向考生 ${selectedCandidate.value.name} 发送警告通知。`)
  }
}

function forceSubmit() {
  if (selectedCandidate.value) {
    alert(`已强制提交考生 ${selectedCandidate.value.name} 的试卷。`)
    selectedCandidate.value = null
  }
}

function resumeCandidate() {
  if (selectedCandidate.value) {
    alert(`已恢复考生 ${selectedCandidate.value.name} 的考试。`)
  }
}

async function refreshData() {
  try {
    const id = effectiveExamId.value
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

onMounted(async () => {
  // If no examId in route, auto-detect the active exam
  if (!routeExamId.value) {
    autoDetecting.value = true
    try {
      const sessions = await fetchExamSessions()
      const active = (sessions || []).find(s => s.status === 'active')
      if (active) {
        detectedExamId.value = active.id
      }
    } catch (e) {
      console.error('Failed to auto-detect active exam:', e)
    } finally {
      autoDetecting.value = false
    }
  }
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

/* Candidate Filters */
.monitor-page__candidate-filters {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  gap: 12px;
}

.monitor-page__filter-tabs {
  display: flex;
  gap: 4px;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 3px;
}

.monitor-page__filter-tab {
  background: none;
  border: none;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 5px;
}

.monitor-page__filter-tab:hover {
  color: #334155;
}

.monitor-page__filter-tab--active {
  background: #fff;
  color: #1e293b;
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
}

.monitor-page__filter-tab-count {
  font-size: 11px;
  background: #e2e8f0;
  color: #64748b;
  padding: 1px 6px;
  border-radius: 8px;
  min-width: 18px;
  text-align: center;
}

.monitor-page__filter-tab--active .monitor-page__filter-tab-count {
  background: #4a6cf7;
  color: #fff;
}

.monitor-page__candidate-search {
  width: 180px;
  padding: 7px 12px;
  font-size: 12px;
  color: #1e293b;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  background: #fff;
  outline: none;
  transition: border-color 0.15s ease;
}

.monitor-page__candidate-search::placeholder {
  color: #cbd5e1;
}

.monitor-page__candidate-search:focus {
  border-color: #4a6cf7;
  box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.08);
}

.monitor-page__candidate-empty {
  text-align: center;
  padding: 40px 20px;
  color: #94a3b8;
  font-size: 13px;
  grid-column: 1 / -1;
}

.monitor-page__candidate-card--selected {
  border-color: #4a6cf7;
  box-shadow: 0 0 0 2px rgba(74, 108, 247, 0.15);
}

/* Activity Timeline */
.monitor-page__timeline {
  position: relative;
}

.monitor-page__timeline-item {
  position: relative;
  display: flex;
  gap: 10px;
  padding-bottom: 14px;
}

.monitor-page__timeline-item:last-child {
  padding-bottom: 0;
}

.monitor-page__timeline-item:last-child .monitor-page__timeline-line {
  display: none;
}

.monitor-page__timeline-marker {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  z-index: 1;
}

.monitor-page__timeline-item--warning .monitor-page__timeline-marker {
  background: #fef3c7;
}

.monitor-page__timeline-icon {
  font-size: 11px;
  line-height: 1;
}

.monitor-page__timeline-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
  flex: 1;
}

.monitor-page__timeline-time {
  font-size: 11px;
  color: #94a3b8;
}

.monitor-page__timeline-text {
  font-size: 13px;
  color: #334155;
  line-height: 1.4;
}

.monitor-page__timeline-candidate {
  font-size: 11px;
  color: #4a6cf7;
  font-weight: 500;
}

.monitor-page__timeline-line {
  position: absolute;
  left: 10px;
  top: 22px;
  bottom: 0;
  width: 1px;
  background: #e2e8f0;
}

/* Detail Panel */
.monitor-page__panel-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
}

.monitor-page__detail-panel {
  width: 420px;
  max-width: 90vw;
  height: 100vh;
  background: #fff;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  animation: slide-in-right 0.25s ease-out;
}

@keyframes slide-in-right {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.monitor-page__detail-panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 24px 24px 0;
  position: sticky;
  top: 0;
  background: #fff;
  z-index: 1;
}

.monitor-page__detail-panel-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.monitor-page__detail-panel-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}

.monitor-page__detail-panel-name {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 2px;
}

.monitor-page__detail-panel-status-text {
  font-size: 12px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
}

.monitor-page__detail-panel-status {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 4px;
  vertical-align: middle;
}

.monitor-page__detail-panel-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color 0.15s;
}

.monitor-page__detail-panel-close:hover {
  color: #475569;
}

.monitor-page__detail-section {
  padding: 18px 24px 0;
}

.monitor-page__detail-section-title {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 12px;
}

/* Risk Score */
.monitor-page__risk-bar-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.monitor-page__risk-bar {
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.monitor-page__risk-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.monitor-page__risk-bar-fill--low { background: #22c55e; }
.monitor-page__risk-bar-fill--mid { background: #f59e0b; }
.monitor-page__risk-bar-fill--high { background: #ef4444; }

.monitor-page__risk-score {
  font-size: 18px;
  font-weight: 700;
  flex-shrink: 0;
}

.monitor-page__risk-score--low { color: #22c55e; }
.monitor-page__risk-score--mid { color: #f59e0b; }
.monitor-page__risk-score--high { color: #ef4444; }

.monitor-page__risk-factors {
  display: flex;
  gap: 20px;
  margin-bottom: 4px;
}

.monitor-page__risk-factor {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.monitor-page__risk-factor-label {
  font-size: 11px;
  color: #94a3b8;
}

.monitor-page__risk-factor-value {
  font-size: 13px;
  font-weight: 600;
  color: #334155;
}

/* Exam Progress in Detail */
.monitor-page__detail-progress {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.monitor-page__detail-progress-label {
  font-size: 12px;
  color: #64748b;
}

.monitor-page__detail-progress-value {
  font-size: 12px;
  color: #334155;
  font-weight: 600;
}

.monitor-page__detail-progress-bar {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.monitor-page__detail-progress-fill {
  height: 100%;
  background: #4a6cf7;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.monitor-page__detail-progress-meta {
  display: flex;
  font-size: 12px;
  color: #94a3b8;
  gap: 16px;
}

/* Behavior Log */
.monitor-page__behavior-list {
  max-height: 180px;
  overflow-y: auto;
}

.monitor-page__behavior-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid #f8fafc;
}

.monitor-page__behavior-item:last-child {
  border-bottom: none;
}

.monitor-page__behavior-icon {
  font-size: 13px;
  flex-shrink: 0;
  margin-top: 1px;
}

.monitor-page__behavior-time {
  font-size: 11px;
  color: #94a3b8;
  flex-shrink: 0;
  font-family: monospace;
}

.monitor-page__behavior-text {
  font-size: 12px;
  color: #334155;
  line-height: 1.4;
}

.monitor-page__behavior-empty {
  font-size: 12px;
  color: #94a3b8;
  text-align: center;
  padding: 16px 0;
}

/* Submissions */
.monitor-page__submission-list {
  max-height: 160px;
  overflow-y: auto;
}

.monitor-page__submission-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 0;
  border-bottom: 1px solid #f8fafc;
  font-size: 12px;
}

.monitor-page__submission-item:last-child {
  border-bottom: none;
}

.monitor-page__submission-time {
  color: #94a3b8;
  font-family: monospace;
  flex-shrink: 0;
}

.monitor-page__submission-question {
  color: #475569;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.monitor-page__submission-result {
  font-weight: 600;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 3px;
  flex-shrink: 0;
}

.monitor-page__submission-result--pass {
  background: rgba(34, 197, 94, 0.1);
  color: #16a34a;
}

.monitor-page__submission-result--fail {
  background: rgba(239, 68, 68, 0.08);
  color: #dc2626;
}

.monitor-page__submission-score {
  color: #64748b;
  flex-shrink: 0;
}

/* Detail Actions */
.monitor-page__detail-actions {
  display: flex;
  gap: 10px;
  padding: 20px 24px 28px;
  margin-top: auto;
  border-top: 1px solid #f1f5f9;
}

.monitor-page__detail-action {
  flex: 1;
  padding: 9px 12px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 7px;
  border: 1px solid;
  cursor: pointer;
  transition: all 0.15s ease;
}

.monitor-page__detail-action--warn {
  background: #fef3c7;
  color: #b45309;
  border-color: #fde68a;
}

.monitor-page__detail-action--warn:hover {
  background: #fde68a;
}

.monitor-page__detail-action--submit {
  background: #fee2e2;
  color: #dc2626;
  border-color: #fecaca;
}

.monitor-page__detail-action--submit:hover {
  background: #fecaca;
}

.monitor-page__detail-action--resume {
  background: #d1fae5;
  color: #059669;
  border-color: #a7f3d0;
}

.monitor-page__detail-action--resume:hover {
  background: #a7f3d0;
}
</style>
