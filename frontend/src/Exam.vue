<template>
  <div id="exam">
    <!-- Loading overlay -->
    <div v-if="loading" id="exam-loading">
      <div class="spinner"></div>
      <div class="loading-text">{{ loadingText }}</div>
    </div>

    <!-- Exam UI -->
    <template v-else>
      <div id="exam-topbar">
        <span class="exam-title">{{ article.title }}</span>
        <button class="back-btn" @click="finish">← 返回</button>
        <span class="exam-timer" :class="{ warn: examTime <= 300 }">
          {{ formatTime(examTime) }}
        </span>
        <button class="finish-btn" @click="finish">完成考试</button>
      </div>
      <iframe id="exam-frame" :src="examUrl" frameborder="0"></iframe>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  article: { type: Object, required: true }
})
const emit = defineEmits(['finish'])

const API_BASE = 'http://localhost:8000'

const loading = ref(true)
const loadingText = ref('正在准备考试环境...')
const port = ref(null)
const examTime = ref(7200)
let timer = null

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

const finish = () => {
  clearInterval(timer)
  timer = null
  emit('finish')
}

onMounted(async () => {
  try {
    const res = await fetch(`${API_BASE}/create_env`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getHeaders() },
      body: JSON.stringify({
        image: 'codesandbox-image-new:latest',
        article: props.article.filename.replace('.md', '')
      })
    })
    const data = await res.json()
    port.value = data.port
    loading.value = false
    startTimer()
  } catch (e) {
    console.error('Failed to create environment:', e)
    loadingText.value = '环境创建失败，请重试'
  }
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
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: #f8fafc;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #4a6cf7;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: #64748b;
  margin-top: 16px;
  font-size: 14px;
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
  color: #e94560;
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  50% { opacity: 0.5; }
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
#exam-frame {
  flex: 1;
  width: 100%;
  border: none;
  display: block;
}
</style>
