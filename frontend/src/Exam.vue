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
        <button class="back-btn" @click="finish">← 返回</button>
        <span class="exam-timer" :class="{ warn: examTime <= 300 }">
          {{ formatTime(examTime) }}
        </span>
        <button class="submit-btn" @click="submitTest">提交测试</button>
        <button class="finish-btn" @click="finish">完成考试</button>
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

const submitTest = () => {
  // TODO: 待实现提交逻辑
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

  router.push({ name: 'home' })
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
    router.push({ name: 'home' })
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

  // Step 3: 记录考试时间（不轮询，由 iframe 错误兜底）
  setStep(2, 'current')
  addLog('容器已创建，正在进入环境...')

  addLog('正在记录考试状态...')
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
    }
  } catch (e) {
    console.error('Failed to record exam start:', e)
    addLog('使用默认考试时间')
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
  height: 100vh;
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
</style>
