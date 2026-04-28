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
  background: #1a1a2e;
}

/* Loading */
#exam-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #0f3460;
  border-top-color: #e94560;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: #fff;
  margin-top: 20px;
  font-size: 16px;
}

/* Topbar */
#exam-topbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0 20px;
  height: 56px;
  background: #16213e;
  border-bottom: 1px solid #0f3460;
  flex-shrink: 0;
}

.exam-title {
  color: #fff;
  font-weight: bold;
  font-size: 16px;
  margin-right: auto;
}

.back-btn {
  padding: 6px 14px;
  background: #0f3460;
  color: #a0a0a0;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.back-btn:hover {
  background: #1a4a7a;
  color: #fff;
}

.exam-timer {
  color: #4ecca3;
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
  padding: 8px 20px;
  background: #e94560;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.finish-btn:hover {
  background: #c73650;
}

/* Iframe */
#exam-frame {
  flex: 1;
  width: 100%;
  border: none;
  display: block;
}
</style>
