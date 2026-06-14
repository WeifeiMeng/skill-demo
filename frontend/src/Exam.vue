<template>
  <div id="exam">
    <!-- Loading overlay -->
    <div v-if="loading" id="exam-loading">
      <div class="loading-card">
        <div class="loading-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M4 16c0 2.5 2 4 8 4s8-1.5 8-4m0-8c0-2.5-2-4-8-4s-8 1.5-8 4m16 0v8m-16-8v8m16-4c0 2.5-2 4-8 4s-8-1.5-8-4"/>
          </svg>
        </div>
        <div class="loading-title">正在准备考试环境</div>

        <div class="loading-steps">
          <div
            v-for="(step, i) in steps"
            :key="i"
            class="step"
            :class="{
              'step-past': step.status === 'done',
              'step-current': step.status === 'current',
              'step-future': step.status === 'pending'
            }"
          >
            <div class="step-indicator">
              <span v-if="step.status === 'done'" class="step-check">✓</span>
              <span v-else-if="step.status === 'current'" class="step-dot"></span>
              <span v-else class="step-num">{{ i + 1 }}</span>
            </div>
            <div class="step-label">{{ step.label }}</div>
          </div>
        </div>

        <div v-if="stepLogs.length" class="loading-logs">
          <div v-for="(log, i) in stepLogs" :key="i" class="log-line">{{ log }}</div>
          <div class="log-cursor">_</div>
        </div>

        <div class="loading-hint">{{ loadingText }}</div>
      </div>
    </div>

    <!-- Exam UI -->
    <template v-else>
      <div id="exam-topbar">
        <span class="exam-title">{{ article?.title || '考试中' }}</span>
        <button class="back-btn" @click="goBack">← 返回</button>
        <span class="exam-timer" :class="{ warn: examTime <= 300 }">
          {{ formatTime(examTime) }}
        </span>
        <button class="submit-btn" :disabled="submitting" @click="submitTest">
          {{ submitting ? '评测中...' : '提交测试' }}
        </button>
        <button class="finish-btn" @click="finish">完成考试</button>
      </div>

      <!-- Test result overlay -->
      <div v-if="testResult" class="result-overlay">
        <div class="result-card">
          <div class="result-header">
            <span class="result-title">测试结果</span>
            <button class="result-close" @click="testResult = null">&times;</button>
          </div>
          <div class="result-score">
            <span class="score-num" :class="{ 'score-fail': !testResult.passed }">{{ testResult.score }}</span>
            <span class="score-max">/ {{ testResult.max_score }}</span>
            <span class="score-badge" :class="testResult.passed ? 'badge-pass' : 'badge-fail'">
              {{ testResult.passed ? 'PASS' : 'FAIL' }}
            </span>
          </div>
          <div class="result-cases">
            <div
              v-for="(c, i) in testResult.cases"
              :key="i"
              class="result-case"
              :class="c.passed ? 'case-pass' : 'case-fail'"
            >
              <span class="case-icon">{{ c.passed ? '✓' : '✗' }}</span>
              <span class="case-name">{{ c.name }}</span>
              <span class="case-msg" v-if="c.message">{{ c.message }}</span>
            </div>
          </div>
        </div>
      </div>
      <div id="exam-frame-wrap">
        <iframe
          v-show="!iframeError"
          :key="iframeKey"
          id="exam-frame"
          :src="examUrl"
          frameborder="0"
          @error="iframeError = true"
        ></iframe>
        <!-- Iframe 加载失败遮罩 -->
        <div v-if="iframeError" class="iframe-error">
          <div class="error-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 8v4m0 4h.01"/>
            </svg>
          </div>
          <div class="error-title">环境暂未就绪</div>
          <p class="error-desc">容器正在启动，可能还需要几秒钟</p>
          <button class="error-retry-btn" @click="retryIframe">重新加载</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const API_BASE = 'http://localhost:8000'

const article = ref(null)
const loading = ref(true)
const loadingText = ref('')
const port = ref(null)
const containerId = ref(null)
const examTime = ref(7200)
const stepLogs = ref([])
const iframeError = ref(false)
const iframeKey = ref(0)
const submitting = ref(false)
const testResult = ref(null)
let timer = null

const steps = ref([
  { label: '加载题目', status: 'current' },
  { label: '创建容器', status: 'pending' },
  { label: '准备环境', status: 'pending' }
])

const setStep = (index, status) => {
  steps.value[index].status = status
}

const addLog = (msg) => {
  stepLogs.value.push(msg)
}

const getHeaders = () => {
  const t = localStorage.getItem('token')
  return t ? { 'Authorization': `Bearer ${t}` } : {}
}

const examUrl = computed(() => {
  if (!port.value) return ''
  return `http://localhost:${port.value}/?folder=/workspace`
})

const formatTime = (seconds) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) {
    return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  }
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

const startTimer = () => {
  timer = setInterval(() => {
    if (examTime.value > 0) {
      examTime.value--
    } else {
      clearInterval(timer)
      timer = null
    }
  }, 1000)
}

const retryIframe = () => {
  iframeError.value = false
  iframeKey.value++
}

// 容器创建后直接使用，不轮询 - 由 iframe 错误兜底处理

const submitTest = async () => {
  if (submitting.value) return
  submitting.value = true
  testResult.value = null

  try {
    const res = await fetch(`${API_BASE}/exam/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getHeaders() },
      body: JSON.stringify({
        article: route.params.filename,
        container_id: containerId.value
      })
    })
    if (res.ok) {
      testResult.value = await res.json()
    } else {
      const err = await res.json().catch(() => ({}))
      testResult.value = {
        passed: false,
        score: 0,
        max_score: 100,
        cases: [{ name: '请求失败', passed: false, message: err.detail || `HTTP ${res.status}` }]
      }
    }
  } catch (e) {
    testResult.value = {
      passed: false,
      score: 0,
      max_score: 100,
      cases: [{ name: '网络错误', passed: false, message: e.message }]
    }
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  // 返回首页，保留考试状态
  router.push({ name: 'challenges' })
}

const finish = async () => {
  clearInterval(timer)
  timer = null

  // 停止正在运行的 Docker 容器
  if (containerId.value) {
    try {
      await fetch(`${API_BASE}/containers/${containerId.value}/stop`, {
        method: 'POST',
        headers: getHeaders()
      })
    } catch (e) {
      console.error('Failed to stop container:', e)
    }
  }

  // 结束考试会话
  try {
    await fetch(`${API_BASE}/exam/finish?article=${route.params.filename}`, {
      method: 'POST',
      headers: getHeaders()
    })
  } catch (e) {
    console.error('Failed to finish exam:', e)
  }

  router.push({ name: 'completed', params: { filename: route.params.filename } })
}

const loadArticle = async () => {
  const filename = route.params.filename
  addLog(`正在加载题目: ${filename}...`)
  try {
    const res = await fetch(`${API_BASE}/articles`)
    if (res.ok) {
      const articles = await res.json()
      article.value = articles.find(a => a.filename === filename)
      if (!article.value) {
        loadingText.value = '题目未找到'
        addLog('✗ 题目未找到')
        return false
      }
      addLog(`✓ 已加载题目: ${article.value.title}`)
      return true
    }
  } catch (e) {
    console.error('Failed to load article:', e)
    loadingText.value = '加载失败，请重试'
    addLog('✗ 加载题目失败')
    return false
  }
}

onMounted(async () => {
  // Step 1: 加载题目
  const found = await loadArticle()
  if (!found) return
  setStep(0, 'done')

  // Check auth
  const token = localStorage.getItem('token')
  if (!token) {
    router.push({ name: 'challenges' })
    return
  }

  // Step 2: 创建容器
  setStep(1, 'current')
  loadingText.value = '正在创建容器...'
  addLog('正在向 Docker 请求创建容器...')
  try {
    const res = await fetch(`${API_BASE}/create_env`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getHeaders() },
      body: JSON.stringify({
        image: 'ai-coach:1.0',
        article: route.params.filename
      })
    })
    const data = await res.json()
    port.value = data.port
    containerId.value = data.container_id
    addLog(`✓ 容器已创建 (端口: ${data.port})`)
    setStep(1, 'done')
  } catch (e) {
    console.error('Failed to create environment:', e)
    loadingText.value = '环境创建失败，请重试'
    addLog('✗ 容器创建失败')
    return
  }

  // Step 3: 从后端获取考试时间
  setStep(2, 'current')
  addLog('容器已创建，正在进入环境...')

  addLog('正在同步考试时间...')
  let timeOk = false
  try {
    const timeRes = await fetch(`${API_BASE}/exam/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getHeaders() },
      body: JSON.stringify({
        article: route.params.filename,
        container_id: containerId.value
      })
    })
    if (timeRes.ok) {
      const timeData = await timeRes.json()
      examTime.value = timeData.remaining
      addLog(`考试剩余时间: ${Math.floor(timeData.remaining / 60)} 分钟`)
      timeOk = true
    } else {
      const err = await timeRes.json().catch(() => ({}))
      addLog(`✗ 时间同步失败: ${err.detail || timeRes.status}`)
    }
  } catch (e) {
    console.error('Failed to record exam start:', e)
    addLog(`✗ 时间同步失败: ${e.message}`)
  }

  if (!timeOk) {
    // 不静默降级，停在这里让用户看到错误
    loadingText.value = '考试时间同步失败，请刷新页面重试'
    return
  }

  addLog('即将进入考试环境...')
  await new Promise(r => setTimeout(r, 400))

  setStep(2, 'done')
  loading.value = false
  startTimer()
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>

<style scoped>
#exam {
  width: 100%;
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}

/* Loading */
#exam-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: #0f172a;
}

.loading-card {
  width: 420px;
  text-align: center;
}

.loading-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 24px;
  color: #4a6cf7;
  animation: breathe 2s ease-in-out infinite;
}

.loading-icon svg {
  width: 100%;
  height: 100%;
}

@keyframes breathe {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.08); }
}

.loading-title {
  font-size: 20px;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 36px;
  letter-spacing: 1px;
}

/* Steps */
.loading-steps {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 32px;
}

.step {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step + .step {
  margin-left: 0;
}

.step-label {
  font-size: 13px;
  color: #475569;
  transition: color 0.3s;
}

.step-current .step-label {
  color: #4a6cf7;
  font-weight: 600;
}
.step-past .step-label {
  color: #22c55e;
}

.step-indicator {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  transition: all 0.3s;
}

.step-future .step-indicator {
  background: #1e293b;
  color: #475569;
  border: 1px solid #334155;
}

.step-current .step-indicator {
  background: rgba(74, 108, 247, 0.15);
  border: 2px solid #4a6cf7;
  box-shadow: 0 0 12px rgba(74, 108, 247, 0.3);
}

.step-dot {
  width: 8px;
  height: 8px;
  background: #4a6cf7;
  border-radius: 50%;
  animation: pulse-dot 1.2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.4); opacity: 0.6; }
}

.step-past .step-indicator {
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid #22c55e;
}

.step-check {
  color: #22c55e;
}

.step-num {
  color: #475569;
}

/* Logs */
.loading-logs {
  background: #0a0f1a;
  border: 1px solid #1e293b;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 20px;
  text-align: left;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  min-height: 72px;
  max-height: 120px;
  overflow-y: auto;
}

.log-line {
  color: #64748b;
  line-height: 1.8;
}

.log-cursor {
  color: #4a6cf7;
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

.loading-hint {
  color: #64748b;
  font-size: 13px;
}

/* Topbar */
#exam-topbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0 28px;
  height: 60px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.exam-title {
  color: #1e293b;
  font-weight: 600;
  font-size: 15px;
  margin-right: auto;
}

.back-btn {
  padding: 6px 16px;
  background: #f1f5f9;
  color: #64748b;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
}
.back-btn:hover {
  background: #e2e8f0;
  color: #475569;
}

.exam-timer {
  color: #4a6cf7;
  font-size: 24px;
  font-weight: bold;
  font-variant-numeric: tabular-nums;
  letter-spacing: 2px;
  min-width: 100px;
  text-align: center;
}

.exam-timer.warn {
  color: #ef4444;
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  50% { opacity: 0.5; }
}

.submit-btn {
  padding: 8px 22px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.submit-btn:hover {
  opacity: 0.9;
}

.finish-btn {
  padding: 8px 22px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.finish-btn:hover {
  opacity: 0.9;
}

/* Iframe */
#exam-frame-wrap {
  flex: 1;
  display: flex;
  position: relative;
}

#exam-frame {
  flex: 1;
  width: 100%;
  border: none;
  display: block;
}

.iframe-error {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  gap: 12px;
}

.error-icon {
  width: 48px;
  height: 48px;
  color: #f59e0b;
}

.error-icon svg {
  width: 100%;
  height: 100%;
}

.error-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.error-desc {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

.error-retry-btn {
  margin-top: 4px;
  padding: 10px 28px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.error-retry-btn:hover {
  opacity: 0.9;
}

/* Submit button */
.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Test result overlay */
.result-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.result-card {
  width: 480px;
  max-height: 70vh;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #e2e8f0;
}

.result-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.result-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f1f5f9;
  border-radius: 8px;
  font-size: 18px;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.result-close:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.result-score {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.score-num {
  font-size: 42px;
  font-weight: 800;
  color: #22c55e;
}
.score-num.score-fail {
  color: #ef4444;
}

.score-max {
  font-size: 20px;
  color: #94a3b8;
  font-weight: 500;
}

.score-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 700;
  margin-left: 8px;
}
.badge-pass {
  background: #dcfce7;
  color: #16a34a;
}
.badge-fail {
  background: #fef2f2;
  color: #dc2626;
}

.result-cases {
  padding: 16px 24px 24px;
  overflow-y: auto;
  max-height: 40vh;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-case {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 14px;
}

.case-pass {
  background: #f0fdf4;
}
.case-fail {
  background: #fef2f2;
}

.case-icon {
  font-weight: 700;
  font-size: 15px;
  flex-shrink: 0;
  margin-top: 1px;
}
.case-pass .case-icon {
  color: #22c55e;
}
.case-fail .case-icon {
  color: #ef4444;
}

.case-name {
  color: #334155;
  flex: 1;
}

.case-msg {
  color: #94a3b8;
  font-size: 12px;
  word-break: break-all;
}
</style>
