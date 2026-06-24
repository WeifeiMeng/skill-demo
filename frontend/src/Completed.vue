<template>
  <div class="completed-page">
    <!-- Loading / Error States -->
    <div v-if="loading" class="loading-state">
      <p>加载成绩报告中...</p>
    </div>
    <div v-else-if="loadError" class="error-state">
      <p>{{ loadError }}</p>
      <button class="back-home-btn" @click="$router.push({ name: 'challenges' })">返回首页</button>
    </div>

    <template v-else-if="report">
      <!-- Header Section -->
      <div class="score-header">
        <div class="score-display">
          <span class="score-number" :style="{ color: scoreColor }">{{ report.totalScore }}</span>
          <span class="score-max">/ {{ report.maxScore }}</span>
        </div>
        <StatusBadge :label="gradeLabel" :variant="gradeVariant" />
        <p class="score-subtitle" v-if="report.title || challengeName">{{ report.title || challengeName }}</p>
      </div>

      <!-- Two-Column Detail Grid -->
      <div class="detail-grid">
        <div class="detail-left">
          <div class="detail-card">
            <CircleProgress
              :value="report.resultScore"
              :max="report.resultMax"
              :size="160"
            />
            <p class="detail-label">结果得分</p>
          </div>
        </div>
        <div class="detail-right">
          <div class="process-list">
            <ProcessBar
              v-for="(item, idx) in report.processScores"
              :key="idx"
              :icon="item.icon"
              :label="item.label"
              :score="item.score"
              :max="item.max"
            />
          </div>
        </div>
      </div>

      <!-- Test Cases Section -->
      <div class="section-card">
        <h3 class="section-title">测试用例结果</h3>
        <div v-if="!report.testCases || report.testCases.length === 0" class="section-empty">暂无测试数据</div>
        <div
          v-for="(tc, idx) in report.testCases"
          :key="idx"
          class="test-case-row"
          :class="tc.passed ? 'test-case--pass' : 'test-case--fail'"
        >
          <span class="test-dot" :class="tc.passed ? 'dot--pass' : 'dot--fail'"></span>
          <div class="test-info">
            <span class="test-name">{{ tc.name }}</span>
            <span class="test-message">{{ tc.message }}</span>
          </div>
        </div>
      </div>

      <!-- Submitted Code Section -->
      <div class="section-card">
        <h3 class="section-title">提交代码</h3>
        <CodeBlock :code="submittedCode" :highlights="[]" />
        <div class="code-meta-row">
          <span class="code-meta-item">用时: {{ meta.duration }}</span>
          <span class="code-meta-item">AI轮次: {{ meta.aiRounds }}</span>
          <span class="code-meta-item">Token消耗: {{ meta.tokensUsed }}</span>
          <span class="code-meta-item">模型: {{ meta.model }}</span>
          <span class="code-meta-item">切屏次数: {{ meta.tabSwitches }}</span>
        </div>
      </div>

      <!-- Bottom Stats Bar -->
      <div class="bottom-stats">
        <div class="bottom-stat">
          <span class="bottom-stat-label">总用时</span>
          <span class="bottom-stat-value">{{ meta.duration }}</span>
        </div>
        <div class="bottom-stat">
          <span class="bottom-stat-label">AI交互轮次</span>
          <span class="bottom-stat-value">{{ meta.aiRounds }}</span>
        </div>
        <div class="bottom-stat">
          <span class="bottom-stat-label">Token消耗</span>
          <span class="bottom-stat-value">{{ meta.tokensUsed }}</span>
        </div>
        <div class="bottom-stat">
          <span class="bottom-stat-label">切屏次数</span>
          <span class="bottom-stat-value">{{ meta.tabSwitches }}</span>
        </div>
      </div>

      <!-- Back Button -->
      <div class="back-row">
        <button class="back-home-btn" @click="$router.push({ name: 'challenges' })">返回首页</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import CircleProgress from './components/CircleProgress.vue'
import ProcessBar from './components/ProcessBar.vue'
import StatusBadge from './components/StatusBadge.vue'
import CodeBlock from './components/CodeBlock.vue'
import { fetchScoreReport } from './data/api.js'

const route = useRoute()

const report = ref(null)
const loading = ref(true)
const loadError = ref('')
const challengeName = ref('')

// --- Derived: Submitted Code (handles both `submittedCode` and `code` fields) ---
const submittedCode = computed(() => {
  if (!report.value) return ''
  return report.value.submittedCode || report.value.code || ''
})

// --- Derived: Metadata (handles both `metadata` and `stats` shapes) ---
const meta = computed(() => {
  if (!report.value) return {}
  const m = report.value.metadata || report.value.stats || {}
  return {
    duration: m.duration || m.timeUsed || '-',
    aiRounds: m.aiRounds ?? '-',
    tokensUsed: m.tokensUsed ?? m.tokens ?? '-',
    model: m.model || '-',
    tabSwitches: m.tabSwitches ?? '-'
  }
})

// --- Grade ---
const gradeLabel = computed(() => {
  if (!report.value) return ''
  const score = report.value.totalScore ?? 0
  if (score >= 80) return '优秀'
  if (score >= 60) return '良好'
  if (score >= 50) return '及格'
  return '不及格'
})

const gradeVariant = computed(() => {
  if (!report.value) return 'default'
  const score = report.value.totalScore ?? 0
  if (score >= 80) return 'pass'
  if (score >= 60) return 'pass'
  if (score >= 50) return 'pending'
  return 'fail'
})

const scoreColor = computed(() => {
  if (!report.value) return '#1e293b'
  const score = report.value.totalScore ?? 0
  if (score >= 80) return '#22c55e'
  if (score >= 50) return '#f59e0b'
  return '#ef4444'
})

// --- Load ---
onMounted(async () => {
  loading.value = true
  loadError.value = ''
  try {
    const filename = route.params.filename
    if (!filename) {
      loadError.value = '未找到考试文件名'
      return
    }
    const data = await fetchScoreReport(filename)
    if (!data) {
      loadError.value = '无法加载成绩数据'
      return
    }
    report.value = data
    challengeName.value = filename
  } catch (e) {
    console.error('Failed to load score report:', e)
    loadError.value = '加载成绩报告失败，请稍后重试'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.completed-page {
  min-height: 100vh;
  background: #f8fafc;
  padding: 48px 24px 60px;
  max-width: 900px;
  margin: 0 auto;
}

/* --- States --- */
.loading-state,
.error-state {
  text-align: center;
  padding: 80px 20px;
  color: #64748b;
  font-size: 15px;
}

.error-state {
  color: #ef4444;
}

/* --- Score Header --- */
.score-header {
  text-align: center;
  margin-bottom: 36px;
}

.score-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
  margin-bottom: 12px;
}

.score-number {
  font-size: 64px;
  font-weight: 800;
  line-height: 1.1;
}

.score-max {
  font-size: 20px;
  color: #94a3b8;
  font-weight: 500;
}

.score-subtitle {
  margin-top: 12px;
  font-size: 14px;
  color: #64748b;
}

/* --- Detail Grid --- */
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.detail-left {
  display: flex;
  justify-content: center;
}

.detail-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.detail-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
  margin: 0;
}

.detail-right {
  display: flex;
  align-items: center;
}

.process-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

/* --- Section Cards --- */
.section-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px;
}

.section-empty {
  color: #94a3b8;
  font-size: 13px;
  text-align: center;
  padding: 16px 0;
}

/* --- Test Cases --- */
.test-case-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 14px;
  border-left: 3px solid transparent;
  margin-bottom: 2px;
  border-radius: 0 8px 8px 0;
}

.test-case--pass {
  border-left-color: #22c55e;
  background: #f0fdf4;
}

.test-case--fail {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.test-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}

.dot--pass {
  background: #22c55e;
}

.dot--fail {
  background: #ef4444;
}

.test-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.test-name {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.test-message {
  font-size: 12px;
  color: #64748b;
}

/* --- Code Meta --- */
.code-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 20px;
  margin-top: 14px;
}

.code-meta-item {
  font-size: 13px;
  color: #64748b;
}

/* --- Bottom Stats --- */
.bottom-stats {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 8px;
  margin-bottom: 36px;
  flex-wrap: wrap;
}

.bottom-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px 24px;
  min-width: 120px;
  flex: 1;
}

.bottom-stat-label {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.bottom-stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #4a6cf7;
}

/* --- Back Button --- */
.back-row {
  text-align: center;
}

.back-home-btn {
  padding: 12px 36px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}
.back-home-btn:hover {
  opacity: 0.9;
}

/* --- Responsive --- */
@media (max-width: 700px) {
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  .detail-left {
    justify-content: center;
  }
  .detail-right {
    justify-content: center;
  }
  .bottom-stats {
    flex-direction: column;
  }
  .score-number {
    font-size: 48px;
  }
}
</style>
