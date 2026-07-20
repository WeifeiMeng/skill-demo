<template>
  <AdminLayout activeRoute="grading">
    <div class="grading-page">
      <!-- No exam ID -->
      <div v-if="!effectiveExamId && !autoDetecting" class="grading-page__no-exam">
        <p>当前没有已结束的考试场次。</p>
        <router-link to="/admin/exams" class="grading-page__back-link">前往考试管理</router-link>
      </div>
      <div v-else-if="autoDetecting" class="grading-page__loading">
        <div class="grading-page__loading-spinner"></div>
        <span>正在查找已结束的考试...</span>
      </div>

      <template v-else>
        <!-- Header -->
        <div class="grading-page__header">
          <h1 class="grading-page__title">成绩与阅卷</h1>
          <span class="grading-page__exam-name">{{ examName }}</span>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="grading-page__loading">
          <div class="grading-page__loading-spinner"></div>
          <span>加载成绩数据...</span>
        </div>

        <template v-else>
          <!-- Stat Cards -->
          <div class="grading-page__stats">
            <StatCard label="参考人数" :value="stats.participantCount" color="blue" />
            <StatCard label="通过率" :value="stats.passRate + '%'" color="green" />
            <StatCard label="平均分" :value="stats.avgScore" color="amber" />
            <StatCard
              label="待阅卷"
              :value="stats.pendingReview"
              :color="stats.pendingReview > 0 ? 'red' : 'green'"
            />
          </div>

          <!-- Tab Bar -->
          <div class="grading-page__tabs">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="grading-page__tab"
              :class="{ 'grading-page__tab--active': activeTab === tab.key }"
              @click="activeTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>

          <!-- Tab 1: 成绩总览 -->
          <div v-if="activeTab === 'overview'" class="grading-page__tab-content">
            <!-- Distribution Chart -->
            <div class="grading-page__card">
              <h3 class="grading-page__card-title">分数分布</h3>
              <div class="grading-page__chart">
                <div
                  v-for="d in distribution"
                  :key="d.range"
                  class="grading-page__bar-col"
                >
                  <div class="grading-page__bar-wrapper">
                    <div
                      class="grading-page__bar"
                      :style="{ height: maxCount > 0 ? (d.count / maxCount * 100) + '%' : '0%' }"
                    >
                      <span class="grading-page__bar-tooltip">{{ d.count }} 人</span>
                    </div>
                  </div>
                  <span class="grading-page__bar-label">{{ d.range }}</span>
                </div>
              </div>
            </div>

            <!-- Scores Table -->
            <div class="grading-page__card">
              <h3 class="grading-page__card-title">学员成绩</h3>
              <div class="grading-page__table-wrap">
                <table class="grading-page__table">
                  <thead>
                    <tr>
                      <th>排名</th>
                      <th>姓名</th>
                      <th v-for="i in maxQuestions" :key="i">题目 {{ i }}</th>
                      <th>总分</th>
                      <th>状态</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="s in scores" :key="s.rank">
                      <td>
                        <span class="grading-page__rank" :class="rankClass(s.rank)">{{ s.rank }}</span>
                      </td>
                      <td class="grading-page__table-name">{{ s.name }}</td>
                      <td v-for="i in maxQuestions" :key="i">
                        <ScoreBar
                          :score="getQuestionScore(s, i)"
                          :max="100"
                          :showScore="true"
                        />
                      </td>
                      <td>
                        <span class="grading-page__total-score">{{ s.totalScore }}</span>
                      </td>
                      <td>
                        <StatusBadge
                          :label="scoreStatusLabel(s.status)"
                          :variant="scoreStatusVariant(s.status)"
                        />
                      </td>
                      <td>
                        <button
                          class="grading-page__table-action"
                          @click="activeTab = s.status === 'pending_review' ? 'manual' : 'overview'"
                        >
                          {{ s.status === 'pending_review' ? '阅卷' : '查看' }}
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Tab 2: 分数分布 -->
          <div v-if="activeTab === 'distribution'" class="grading-page__tab-content">
            <div class="grading-page__card">
              <h3 class="grading-page__card-title">分数分布详情</h3>
              <div class="grading-page__chart grading-page__chart--large">
                <div
                  v-for="d in distribution"
                  :key="d.range"
                  class="grading-page__bar-col"
                >
                  <div class="grading-page__bar-wrapper grading-page__bar-wrapper--large">
                    <div
                      class="grading-page__bar grading-page__bar--large"
                      :style="{ height: maxCount > 0 ? (d.count / maxCount * 100) + '%' : '0%' }"
                    >
                      <span class="grading-page__bar-tooltip">{{ d.count }} 人</span>
                    </div>
                  </div>
                  <span class="grading-page__bar-label">{{ d.range }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Tab 3: 人工阅卷 -->
          <div v-if="activeTab === 'manual'" class="grading-page__tab-content">
            <div
              v-for="(review, idx) in pendingReviews"
              :key="idx"
              class="grading-page__review-card"
            >
              <div class="grading-page__review-header">
                <div class="grading-page__review-student">
                  <span class="grading-page__review-name">{{ review.name }}</span>
                  <span class="grading-page__review-rank">排名 #{{ review.rank || idx + 1 }}</span>
                </div>
              </div>

              <div class="grading-page__review-auto">
                <span class="grading-page__review-section-label">自动评分</span>
                <div class="grading-page__review-scores">
                  <div class="grading-page__review-score-item">
                    <span class="grading-page__review-score-name">正确性</span>
                    <ScoreBar :score="review.autoScores.correctness" :max="100" />
                  </div>
                  <div class="grading-page__review-score-item">
                    <span class="grading-page__review-score-name">效率</span>
                    <ScoreBar :score="review.autoScores.efficiency" :max="100" />
                  </div>
                  <div class="grading-page__review-score-item">
                    <span class="grading-page__review-score-name">代码风格</span>
                    <ScoreBar :score="review.autoScores.style" :max="100" />
                  </div>
                </div>
                <div class="grading-page__review-total-auto">
                  自动评分总分: <strong>{{ review.totalAutoScore }}</strong>
                </div>
              </div>

              <div class="grading-page__review-code">
                <span class="grading-page__review-section-label">提交代码</span>
                <CodeBlock :code="review.code" />
              </div>

              <div v-if="review.submitTime || review.attemptCount" class="grading-page__review-meta">
                <span v-if="review.submitTime">提交时间: {{ review.submitTime }}</span>
                <span v-if="review.attemptCount">尝试次数: {{ review.attemptCount }}</span>
              </div>

              <div class="grading-page__review-manual">
                <div class="grading-page__review-manual-field">
                  <label class="grading-page__review-label">手动评分 (0-100)</label>
                  <input
                    type="number"
                    class="grading-page__review-input"
                    min="0"
                    max="100"
                    :value="review.manualScore"
                    @input="updateManualScore(idx, $event)"
                  />
                </div>
                <div class="grading-page__review-manual-field">
                  <label class="grading-page__review-label">评语</label>
                  <textarea
                    class="grading-page__review-textarea"
                    rows="3"
                    placeholder="输入评语..."
                    :value="review.comment"
                    @input="updateComment(idx, $event)"
                  ></textarea>
                </div>
                <div class="grading-page__review-actions">
                  <button class="grading-page__review-draft-btn" @click="saveReviewDraft(idx)">保存草稿</button>
                  <button class="grading-page__review-submit-btn" @click="submitReview(idx)">提交评分</button>
                </div>
              </div>
            </div>

            <div v-if="pendingReviews.length === 0" class="grading-page__empty">
              暂无待阅卷记录
            </div>
          </div>

          <!-- Tab 4: 题目分析 -->
          <div v-if="activeTab === 'analysis'" class="grading-page__tab-content">
            <div class="grading-page__card">
              <div class="grading-page__table-wrap">
                <table class="grading-page__table">
                  <thead>
                    <tr>
                      <th>题目</th>
                      <th>平均分</th>
                      <th>通过率</th>
                      <th>得分分布</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="q in questionAnalysis" :key="q.name">
                      <td class="grading-page__table-name">{{ q.name }}</td>
                      <td>{{ q.avgScore }}</td>
                      <td>
                        <span
                          class="grading-page__pass-rate"
                          :class="{
                            'grading-page__pass-rate--high': q.passRate >= 70,
                            'grading-page__pass-rate--mid': q.passRate >= 40,
                            'grading-page__pass-rate--low': q.passRate < 40,
                          }"
                        >
                          {{ q.passRate }}%
                        </span>
                      </td>
                      <td>
                        <div class="grading-page__mini-bar">
                          <div
                            class="grading-page__mini-bar-fill"
                            :style="{ width: Math.min(q.passRate, 100) + '%' }"
                          ></div>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </template>
      </template>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AdminLayout from './components/AdminLayout.vue'
import StatCard from './components/StatCard.vue'
import StatusBadge from './components/StatusBadge.vue'
import ScoreBar from './components/ScoreBar.vue'
import CodeBlock from './components/CodeBlock.vue'
import { fetchGradingData, fetchExamSessions } from './data/api.js'

const route = useRoute()
const routeExamId = computed(() => route.params.examId)
const detectedExamId = ref(null)
const autoDetecting = ref(false)
const effectiveExamId = computed(() => routeExamId.value || detectedExamId.value)
const examName = ref('')
const loading = ref(true)
const activeTab = ref('overview')

const tabs = [
  { key: 'overview', label: '成绩总览' },
  { key: 'distribution', label: '分数分布' },
  { key: 'manual', label: '人工阅卷' },
  { key: 'analysis', label: '题目分析' },
]

const stats = reactive({
  participantCount: 0,
  passRate: 0,
  avgScore: 0,
  pendingReview: 0,
})

const distribution = ref([])
const scores = ref([])
const pendingReviews = ref([])
const questionAnalysis = ref([])

const maxQuestions = computed(() => {
  if (scores.value.length === 0) return 4
  return Math.max(...scores.value.map((s) => (s.questionScores ? s.questionScores.length : 0)), 4)
})

const maxCount = computed(() => {
  if (distribution.value.length === 0) return 1
  return Math.max(...distribution.value.map((d) => d.count), 1)
})

function scoreStatusLabel(status) {
  const map = { passed: '通过', failed: '未通过', pending_review: '待阅卷' }
  return map[status] || status
}

function scoreStatusVariant(status) {
  const map = { passed: 'pass', failed: 'fail', pending_review: 'pending_review' }
  return map[status] || 'default'
}

function rankClass(rank) {
  if (rank === 1) return 'grading-page__rank--gold'
  if (rank === 2) return 'grading-page__rank--silver'
  if (rank === 3) return 'grading-page__rank--bronze'
  return ''
}

function getQuestionScore(student, index) {
  if (student.questionScores && student.questionScores.length >= index) {
    return student.questionScores[index - 1]
  }
  // Fallback for mock data with t1, t2, etc.
  return student['t' + index] ?? 0
}

function updateManualScore(idx, event) {
  pendingReviews.value[idx].manualScore = Number(event.target.value) || 0
}

function updateComment(idx, event) {
  pendingReviews.value[idx].comment = event.target.value
}

function saveReviewDraft(idx) {
  const review = pendingReviews.value[idx]
  alert(`草稿已保存: ${review.name} - 评分 ${review.manualScore || '-'}`)
}

function submitReview(idx) {
  const review = pendingReviews.value[idx]
  if (!review.manualScore) {
    alert('请先输入手动评分')
    return
  }
  alert(`评分已提交: ${review.name} - ${review.manualScore} 分`)
  pendingReviews.value.splice(idx, 1)
  stats.pendingReview = Math.max(0, stats.pendingReview - 1)
}

function generateQuestionAnalysis() {
  const questions = ['LRU 缓存设计', '二叉树遍历优化', '图最短路径算法', '动态规划综合题']
  return questions.map((name) => ({
    name,
    avgScore: Math.round(50 + Math.random() * 40),
    passRate: Math.round(40 + Math.random() * 50),
  }))
}

async function loadData() {
  loading.value = true
  try {
    const id = effectiveExamId.value
    if (!id) return

    const result = await fetchGradingData(id)

    examName.value = result.examName || result.title || ''

    // Stats
    stats.participantCount = result.stats?.participantCount ?? result.stats?.totalParticipants ?? 0
    stats.passRate = result.stats?.passRate ?? 0
    stats.avgScore = result.stats?.avgScore ?? 0
    stats.pendingReview = result.stats?.pendingReview ?? 0

    // Distribution
    distribution.value = result.distribution || []

    // Scores - normalize from mock data (students array with t1-t4) or spec (scores with questionScores)
    const rawScores = result.scores || result.students || []
    scores.value = rawScores.map((s) => {
      if (s.questionScores) {
        return {
          rank: s.rank,
          name: s.name,
          questionScores: s.questionScores,
          totalScore: s.totalScore,
          status: s.status,
        }
      }
      // Flatten t1-t4 into questionScores array
      const qScores = []
      for (let i = 1; i <= 20; i++) {
        if (s['t' + i] !== undefined) qScores.push(s['t' + i])
        else break
      }
      return {
        rank: s.rank,
        name: s.name,
        questionScores: qScores,
        totalScore: s.total,
        status: s.status,
      }
    })

    // Pending reviews - normalize from mock data (gradingDetail single object) or spec (pendingReviews array)
    if (result.pendingReviews && Array.isArray(result.pendingReviews)) {
      pendingReviews.value = result.pendingReviews.map((r) => ({
        ...r,
        manualScore: null,
        comment: '',
      }))
    } else if (result.gradingDetail) {
      const d = result.gradingDetail
      pendingReviews.value = [
        {
          id: 'pr-001',
          name: d.student || d.name,
          rank: d.rank || scores.value.find((s) => s.name === d.student)?.rank || '-',
          autoScores: {
            correctness: d.autoScores?.correctness ?? 0,
            efficiency: d.autoScores?.efficiency ?? d.autoScores?.performance ?? 0,
            style: d.autoScores?.style ?? 0,
          },
          totalAutoScore: d.totalAutoScore ?? Object.values(d.autoScores || {}).reduce((a, b) => a + b, 0),
          code: d.code || '',
          submitTime: d.meta?.time || '',
          attemptCount: d.meta?.submits || 0,
          manualScore: null,
          comment: '',
        },
      ]
    } else {
      // Generate pending reviews from scores with pending_review status
      pendingReviews.value = scores.value
        .filter((s) => s.status === 'pending_review')
        .map((s) => ({
          id: 'pr-' + s.rank,
          name: s.name,
          rank: s.rank,
          autoScores: { correctness: 40, efficiency: 30, style: 20 },
          totalAutoScore: 90,
          code: '// 代码加载中...',
          submitTime: '',
          attemptCount: 0,
          manualScore: null,
          comment: '',
        }))
    }

    // Question analysis
    questionAnalysis.value = result.questionAnalysis || generateQuestionAnalysis()
  } catch (e) {
    console.error('Failed to load grading data:', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // If no examId in route, auto-detect the most recent ended exam
  if (!routeExamId.value) {
    autoDetecting.value = true
    try {
      const sessions = await fetchExamSessions()
      // Prefer ended exams, fallback to active
      const ended = (sessions || []).filter(s => s.status === 'ended')
      if (ended.length > 0) {
        detectedExamId.value = ended[0].id
      } else {
        const active = (sessions || []).find(s => s.status === 'active')
        if (active) detectedExamId.value = active.id
      }
    } catch (e) {
      console.error('Failed to auto-detect exam:', e)
    } finally {
      autoDetecting.value = false
    }
  }
  loadData()
})
</script>

<style scoped>
.grading-page__no-exam {
  text-align: center;
  padding: 80px 20px;
  color: #64748b;
  font-size: 14px;
}

.grading-page__back-link {
  display: inline-block;
  margin-top: 12px;
  color: #4a6cf7;
  font-weight: 600;
  text-decoration: none;
}

.grading-page__back-link:hover {
  text-decoration: underline;
}

.grading-page__header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}

.grading-page__title {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.grading-page__exam-name {
  font-size: 13px;
  color: #64748b;
  background: #f1f5f9;
  padding: 4px 12px;
  border-radius: 6px;
}

.grading-page__loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 80px 20px;
  color: #64748b;
  font-size: 14px;
}

.grading-page__loading-spinner {
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

.grading-page__empty {
  padding: 40px 20px;
  text-align: center;
  color: #94a3b8;
  font-size: 14px;
}

/* Stats */
.grading-page__stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

/* Tabs */
.grading-page__tabs {
  display: flex;
  gap: 0;
  margin-bottom: 20px;
  border-bottom: 2px solid #e2e8f0;
}

.grading-page__tab {
  background: none;
  border: none;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: color 0.15s ease, border-color 0.15s ease;
}

.grading-page__tab:hover {
  color: #334155;
}

.grading-page__tab--active {
  color: #4a6cf7;
  border-bottom-color: #4a6cf7;
  font-weight: 600;
}

/* Card */
.grading-page__card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 20px;
}

.grading-page__card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 18px;
}

/* Distribution Chart */
.grading-page__chart {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  height: 180px;
  padding-top: 10px;
}

.grading-page__chart--large {
  height: 280px;
}

.grading-page__bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.grading-page__bar-wrapper {
  flex: 1;
  width: 100%;
  max-width: 60px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  position: relative;
}

.grading-page__bar-wrapper--large {
  max-width: 80px;
}

.grading-page__bar {
  width: 100%;
  background: linear-gradient(180deg, #4a6cf7, #6a3de8);
  border-radius: 6px 6px 0 0;
  min-height: 2px;
  position: relative;
  transition: height 0.4s ease;
}

.grading-page__bar--large {
  border-radius: 8px 8px 0 0;
}

.grading-page__bar-tooltip {
  position: absolute;
  top: -24px;
  left: 50%;
  transform: translateX(-50%);
  background: #1e293b;
  color: #fff;
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 4px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.15s ease;
}

.grading-page__bar:hover .grading-page__bar-tooltip {
  opacity: 1;
}

.grading-page__bar-label {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 8px;
  text-align: center;
}

/* Table */
.grading-page__table-wrap {
  overflow-x: auto;
}

.grading-page__table {
  width: 100%;
  border-collapse: collapse;
}

.grading-page__table thead th {
  text-align: left;
  padding: 10px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  white-space: nowrap;
}

.grading-page__table tbody td {
  padding: 12px 14px;
  font-size: 13px;
  color: #334155;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.grading-page__table tbody tr:last-child td {
  border-bottom: none;
}

.grading-page__table tbody tr:hover {
  background: #f8fafc;
}

.grading-page__table-name {
  font-weight: 500;
  color: #1e293b;
}

.grading-page__rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
  color: #1e293b;
  background: #f1f5f9;
}

.grading-page__rank--gold {
  background: #fef3c7;
  color: #b45309;
}

.grading-page__rank--silver {
  background: #f1f5f9;
  color: #64748b;
}

.grading-page__rank--bronze {
  background: #fed7aa;
  color: #c2410c;
}

.grading-page__total-score {
  font-weight: 700;
  color: #1e293b;
  font-size: 14px;
}

.grading-page__table-action {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
  border-radius: 5px;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s ease;
}

.grading-page__table-action:hover {
  background: #e2e8f0;
}

/* Pass Rate */
.grading-page__pass-rate {
  font-weight: 600;
  font-size: 13px;
}

.grading-page__pass-rate--high {
  color: #22c55e;
}

.grading-page__pass-rate--mid {
  color: #f59e0b;
}

.grading-page__pass-rate--low {
  color: #ef4444;
}

/* Mini Bar */
.grading-page__mini-bar {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  min-width: 80px;
}

.grading-page__mini-bar-fill {
  height: 100%;
  background: #4a6cf7;
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* Review Cards */
.grading-page__review-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
}

.grading-page__review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
  padding-bottom: 14px;
  border-bottom: 1px solid #f1f5f9;
}

.grading-page__review-student {
  display: flex;
  align-items: center;
  gap: 10px;
}

.grading-page__review-name {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}

.grading-page__review-rank {
  font-size: 12px;
  color: #64748b;
  background: #f1f5f9;
  padding: 3px 10px;
  border-radius: 12px;
}

.grading-page__review-section-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.grading-page__review-auto {
  margin-bottom: 18px;
}

.grading-page__review-scores {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}

.grading-page__review-score-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.grading-page__review-score-name {
  font-size: 13px;
  color: #475569;
  min-width: 64px;
}

.grading-page__review-total-auto {
  font-size: 13px;
  color: #334155;
}

.grading-page__review-total-auto strong {
  color: #1e293b;
  font-size: 16px;
}

.grading-page__review-code {
  margin-bottom: 14px;
}

.grading-page__review-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 18px;
  font-size: 11px;
  color: #94a3b8;
}

.grading-page__review-manual {
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

.grading-page__review-manual-field {
  margin-bottom: 14px;
}

.grading-page__review-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 6px;
}

.grading-page__review-input {
  width: 120px;
  padding: 8px 12px;
  font-size: 14px;
  color: #1e293b;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  text-align: center;
}

.grading-page__review-input:focus {
  outline: none;
  border-color: #4a6cf7;
  box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.1);
}

.grading-page__review-textarea {
  width: 100%;
  padding: 10px 12px;
  font-size: 13px;
  color: #1e293b;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
}

.grading-page__review-textarea:focus {
  outline: none;
  border-color: #4a6cf7;
  box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.1);
}

.grading-page__review-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 8px;
}

.grading-page__review-draft-btn {
  background: transparent;
  color: #64748b;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  padding: 9px 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.grading-page__review-draft-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.grading-page__review-submit-btn {
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff;
  border: none;
  border-radius: 7px;
  padding: 9px 20px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.grading-page__review-submit-btn:hover {
  opacity: 0.92;
}
</style>
