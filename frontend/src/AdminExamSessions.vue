<template>
  <AdminLayout activeRoute="exams">
    <div class="exams-page">
      <!-- Header -->
      <div class="exams-page__header">
        <h1 class="exams-page__title">考试管理</h1>
        <button class="exams-page__create-btn" @click="showCreateModal = true">
          <span class="exams-page__create-btn-icon">+</span>
          创建考试
        </button>
      </div>

      <!-- Stat Cards -->
      <div v-if="!loading.stats" class="exams-page__stats">
        <StatCard label="总考试场次" :value="stats.total" color="blue" />
        <StatCard label="进行中" :value="stats.active" color="green" />
        <StatCard label="即将开始" :value="stats.upcoming" color="amber" />
        <StatCard label="总参与人数" :value="stats.totalParticipants" color="blue" />
      </div>
      <div v-else class="exams-page__stats">
        <div v-for="i in 4" :key="i" class="exams-page__stat-skeleton"></div>
      </div>

      <!-- Exam List -->
      <div class="exams-page__table-card">
        <div v-if="loading.sessions" class="exams-page__loading">
          <div class="exams-page__loading-spinner"></div>
          <span>加载考试数据...</span>
        </div>
        <div v-else-if="sessions.length === 0" class="exams-page__empty">
          <p>暂无考试数据</p>
        </div>
        <table v-else class="exams-page__table">
          <thead>
            <tr>
              <th>考试名称</th>
              <th>时间窗口</th>
              <th>题目数</th>
              <th>参与人数</th>
              <th>状态</th>
              <th>通过率</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="exam in sessions" :key="exam.id">
              <td class="exams-page__table-name">
                <span class="exams-page__table-name-text">{{ exam.name }}</span>
                <span class="exams-page__table-name-id">{{ exam.id }}</span>
              </td>
              <td>
                <span class="exams-page__table-time">{{ exam.start }} - {{ exam.end }}</span>
              </td>
              <td>{{ exam.questions }}</td>
              <td>{{ exam.participants?.current ?? 0 }} / {{ exam.participants?.total ?? 0 }}</td>
              <td>
                <StatusBadge :label="statusLabel(exam.status)" :variant="statusVariant(exam.status)" />
              </td>
              <td>
                <span
                  class="exams-page__table-passrate"
                  :class="{
                    'exams-page__table-passrate--high': exam.passRate >= 70,
                    'exams-page__table-passrate--mid': exam.passRate >= 40 && exam.passRate < 70,
                    'exams-page__table-passrate--low': exam.passRate < 40,
                  }"
                >
                  {{ exam.passRate }}%
                </span>
              </td>
              <td class="exams-page__table-actions">
                <router-link
                  v-if="exam.status === 'active'"
                  :to="`/admin/monitor/${exam.id}`"
                  class="exams-page__action-btn exams-page__action-btn--primary"
                >
                  监控
                </router-link>
                <button class="exams-page__action-btn" @click="handleEdit(exam)">编辑</button>
                <button class="exams-page__action-btn" @click="handleDetail(exam)">详情</button>
                <button
                  class="exams-page__action-btn exams-page__action-btn--danger"
                  @click="confirmDelete(exam)"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Delete Confirmation Dialog -->
      <div v-if="deleteTarget" class="exams-page__overlay" @click.self="deleteTarget = null">
        <div class="exams-page__confirm-dialog">
          <h3 class="exams-page__confirm-title">确认删除</h3>
          <p class="exams-page__confirm-text">
            确定要删除考试 "<strong>{{ deleteTarget.name }}</strong>" 吗？此操作不可撤销。
          </p>
          <div class="exams-page__confirm-actions">
            <button class="exams-page__confirm-cancel" @click="deleteTarget = null">取消</button>
            <button class="exams-page__confirm-delete" @click="executeDelete">确认删除</button>
          </div>
        </div>
      </div>

      <!-- Exam Detail Modal -->
      <div v-if="detailTarget" class="exams-page__overlay" @click.self="detailTarget = null">
        <div class="exams-page__detail-modal">
          <div class="exams-page__detail-header">
            <h2 class="exams-page__detail-title">{{ detailTarget.name }}</h2>
            <button class="exams-page__detail-close" @click="detailTarget = null">&times;</button>
          </div>
          <div class="exams-page__detail-body">
            <div class="exams-page__detail-grid">
              <div class="exams-page__detail-item">
                <span class="exams-page__detail-label">考试 ID</span>
                <span class="exams-page__detail-value exams-page__detail-value--mono">{{ detailTarget.id }}</span>
              </div>
              <div class="exams-page__detail-item">
                <span class="exams-page__detail-label">状态</span>
                <StatusBadge :label="statusLabel(detailTarget.status)" :variant="statusVariant(detailTarget.status)" />
              </div>
              <div class="exams-page__detail-item">
                <span class="exams-page__detail-label">题目数量</span>
                <span class="exams-page__detail-value">{{ detailTarget.questions }} 题</span>
              </div>
              <div class="exams-page__detail-item">
                <span class="exams-page__detail-label">通过率</span>
                <span
                  class="exams-page__detail-value exams-page__detail-value--passrate"
                  :class="{
                    'exams-page__table-passrate--high': detailTarget.passRate >= 70,
                    'exams-page__table-passrate--mid': detailTarget.passRate >= 40 && detailTarget.passRate < 70,
                    'exams-page__table-passrate--low': detailTarget.passRate < 40,
                  }"
                >
                  {{ detailTarget.passRate }}%
                </span>
              </div>
              <div class="exams-page__detail-item">
                <span class="exams-page__detail-label">开始时间</span>
                <span class="exams-page__detail-value">{{ detailTarget.start }}</span>
              </div>
              <div class="exams-page__detail-item">
                <span class="exams-page__detail-label">结束时间</span>
                <span class="exams-page__detail-value">{{ detailTarget.end }}</span>
              </div>
              <div class="exams-page__detail-item">
                <span class="exams-page__detail-label">已参与人数</span>
                <span class="exams-page__detail-value">{{ detailTarget.participants?.current ?? 0 }} 人</span>
              </div>
              <div class="exams-page__detail-item">
                <span class="exams-page__detail-label">总名额</span>
                <span class="exams-page__detail-value">{{ detailTarget.participants?.total ?? 0 }} 人</span>
              </div>
            </div>
          </div>
          <div class="exams-page__detail-footer">
            <button class="exams-page__detail-btn" @click="detailTarget = null">关闭</button>
          </div>
        </div>
      </div>

      <!-- Create Exam Modal -->
      <div v-if="showCreateModal" class="exams-page__overlay" @click.self="showCreateModal = false">
        <div class="exams-page__modal">
          <h2 class="exams-page__modal-title">创建考试</h2>

          <div class="exams-page__form-group">
            <label class="exams-page__form-label">考试名称</label>
            <input
              v-model="form.name"
              type="text"
              class="exams-page__form-input"
              placeholder="请输入考试名称"
            />
          </div>

          <div class="exams-page__form-row">
            <div class="exams-page__form-group">
              <label class="exams-page__form-label">开始时间</label>
              <input v-model="form.startTime" type="datetime-local" class="exams-page__form-input" />
            </div>
            <div class="exams-page__form-group">
              <label class="exams-page__form-label">结束时间</label>
              <input v-model="form.endTime" type="datetime-local" class="exams-page__form-input" />
            </div>
          </div>

          <div class="exams-page__form-row">
            <div class="exams-page__form-group">
              <label class="exams-page__form-label">考试时长（分钟）</label>
              <input
                v-model.number="form.duration"
                type="number"
                class="exams-page__form-input"
                placeholder="180"
                min="1"
              />
            </div>
            <div class="exams-page__form-group">
              <label class="exams-page__form-label">通过分数线</label>
              <input
                v-model.number="form.passScore"
                type="number"
                class="exams-page__form-input"
                placeholder="60"
                min="0"
                max="100"
              />
            </div>
          </div>

          <div class="exams-page__form-group">
            <label class="exams-page__form-label">关联题目</label>
            <div class="exams-page__challenge-select">
              <label
                v-for="ch in availableChallenges"
                :key="ch.id"
                class="exams-page__challenge-option"
                :class="{ 'exams-page__challenge-option--selected': form.challenges.includes(ch.id) }"
              >
                <input
                  type="checkbox"
                  :value="ch.id"
                  v-model="form.challenges"
                  class="exams-page__challenge-checkbox"
                />
                <span class="exams-page__challenge-tag">{{ ch.title }}</span>
                <span class="exams-page__challenge-difficulty">{{ ch.difficulty }}</span>
              </label>
            </div>
          </div>

          <div class="exams-page__form-group">
            <label class="exams-page__form-label">白名单</label>
            <textarea
              v-model="form.whitelist"
              class="exams-page__form-textarea"
              rows="4"
              placeholder="每行一个邮箱或用户名&#10;user1@example.com&#10;user2@example.com"
            ></textarea>
          </div>

          <div class="exams-page__form-group">
            <label class="exams-page__form-label">防作弊设置</label>
            <div class="exams-page__anti-cheat">
              <label class="exams-page__checkbox-label">
                <input type="checkbox" v-model="form.antiCheat.blockSwitching" />
                <span>禁止切屏</span>
              </label>
              <label class="exams-page__checkbox-label">
                <input type="checkbox" v-model="form.antiCheat.realtimeMonitor" />
                <span>实时监控</span>
              </label>
              <label class="exams-page__checkbox-label">
                <input type="checkbox" v-model="form.antiCheat.aiAnalysis" />
                <span>AI 行为分析</span>
              </label>
            </div>
          </div>

          <div class="exams-page__modal-actions">
            <button class="exams-page__modal-cancel" @click="showCreateModal = false">取消</button>
            <button class="exams-page__modal-draft" @click="saveDraft">保存草稿</button>
            <button class="exams-page__modal-publish" @click="publishExam">发布考试</button>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import AdminLayout from './components/AdminLayout.vue'
import StatCard from './components/StatCard.vue'
import StatusBadge from './components/StatusBadge.vue'
import { fetchExamSessions, fetchExamStats } from './data/api.js'

const stats = ref({ total: 0, active: 0, upcoming: 0, totalParticipants: 0 })
const sessions = ref([])
const loading = reactive({ stats: true, sessions: true })

const showCreateModal = ref(false)
const deleteTarget = ref(null)

const form = reactive({
  name: '',
  startTime: '',
  endTime: '',
  duration: 180,
  passScore: 60,
  challenges: [],
  whitelist: '',
  antiCheat: {
    blockSwitching: true,
    realtimeMonitor: true,
    aiAnalysis: false,
  },
})

const availableChallenges = [
  { id: 'c1', title: 'LRU 缓存设计', difficulty: 'easy' },
  { id: 'c2', title: 'Deep Face Search', difficulty: 'medium' },
  { id: 'c3', title: '高并发短链接系统', difficulty: 'medium' },
  { id: 'c4', title: '运筹优化挑战', difficulty: 'hard' },
  { id: 'c5', title: '实时流处理管道', difficulty: 'medium' },
  { id: 'c6', title: '分布式锁实现', difficulty: 'hard' },
]

const statusLabelMap = { active: '进行中', upcoming: '即将开始', ended: '已结束', draft: '草稿' }
const statusVariantMap = { active: 'active', upcoming: 'upcoming', ended: 'ended', draft: 'draft' }

function statusLabel(status) {
  return statusLabelMap[status] || status
}

function statusVariant(status) {
  return statusVariantMap[status] || 'default'
}

async function loadData() {
  loading.stats = true
  loading.sessions = true
  try {
    const [statsData, sessionsData] = await Promise.all([
      fetchExamStats(),
      fetchExamSessions(),
    ])
    stats.value = {
      total: statsData.total ?? 0,
      active: statsData.active ?? 0,
      upcoming: statsData.upcoming ?? 0,
      totalParticipants: statsData.totalParticipants ?? 0,
    }
    sessions.value = sessionsData || []
  } catch (e) {
    console.error('Failed to load exam data:', e)
  } finally {
    loading.stats = false
    loading.sessions = false
  }
}

function handleEdit(exam) {
  form.name = exam.name
  form.startTime = exam.start
  form.endTime = exam.end
  form.duration = 180
  form.passScore = exam.passRate
  showCreateModal.value = true
}

const detailTarget = ref(null)

function handleDetail(exam) {
  detailTarget.value = exam
}

function confirmDelete(exam) {
  deleteTarget.value = exam
}

function executeDelete() {
  if (deleteTarget.value) {
    sessions.value = sessions.value.filter((s) => s.id !== deleteTarget.value.id)
    deleteTarget.value = null
  }
}

function resetForm() {
  form.name = ''
  form.startTime = ''
  form.endTime = ''
  form.duration = 180
  form.passScore = 60
  form.challenges = []
  form.whitelist = ''
  form.antiCheat = { blockSwitching: true, realtimeMonitor: true, aiAnalysis: false }
}

function saveDraft() {
  alert(`草稿已保存: ${form.name || '(未命名)'}`)
  resetForm()
  showCreateModal.value = false
}

function publishExam() {
  if (!form.name.trim()) {
    alert('请输入考试名称')
    return
  }
  const newExam = {
    id: 'exam-' + Date.now(),
    name: form.name,
    start: form.startTime,
    end: form.endTime,
    questions: form.challenges.length,
    participants: { current: 0, total: 0 },
    status: 'draft',
    passRate: form.passScore,
  }
  sessions.value.unshift(newExam)
  stats.value.total++
  alert(`考试已发布: ${form.name}`)
  resetForm()
  showCreateModal.value = false
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.exams-page__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.exams-page__title {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.exams-page__create-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s ease, transform 0.15s ease;
}

.exams-page__create-btn:hover {
  opacity: 0.92;
  transform: translateY(-1px);
}

.exams-page__create-btn-icon {
  font-size: 18px;
  line-height: 1;
}

.exams-page__stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.exams-page__stat-skeleton {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 20px;
  height: 80px;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.exams-page__table-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.exams-page__loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px 20px;
  color: #64748b;
  font-size: 14px;
}

.exams-page__loading-spinner {
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

.exams-page__empty {
  padding: 60px 20px;
  text-align: center;
  color: #94a3b8;
  font-size: 14px;
}

.exams-page__table {
  width: 100%;
  border-collapse: collapse;
}

.exams-page__table thead th {
  text-align: left;
  padding: 14px 16px;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.exams-page__table tbody td {
  padding: 14px 16px;
  font-size: 13px;
  color: #334155;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.exams-page__table tbody tr:last-child td {
  border-bottom: none;
}

.exams-page__table tbody tr:hover {
  background: #f8fafc;
}

.exams-page__table-name {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.exams-page__table-name-text {
  font-weight: 600;
  color: #1e293b;
}

.exams-page__table-name-id {
  font-size: 11px;
  color: #94a3b8;
  font-family: monospace;
}

.exams-page__table-time {
  font-size: 12px;
  color: #64748b;
}

.exams-page__table-passrate {
  font-weight: 600;
  font-size: 13px;
}

.exams-page__table-passrate--high {
  color: #22c55e;
}

.exams-page__table-passrate--mid {
  color: #f59e0b;
}

.exams-page__table-passrate--low {
  color: #ef4444;
}

.exams-page__table-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.exams-page__action-btn {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
  border-radius: 5px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.15s ease, color 0.15s ease;
  white-space: nowrap;
}

.exams-page__action-btn:hover {
  background: #e2e8f0;
}

.exams-page__action-btn--primary {
  background: rgba(74, 108, 247, 0.1);
  color: #4a6cf7;
  border-color: rgba(74, 108, 247, 0.2);
}

.exams-page__action-btn--primary:hover {
  background: rgba(74, 108, 247, 0.18);
}

.exams-page__action-btn--danger {
  background: transparent;
  color: #ef4444;
  border: none;
}

.exams-page__action-btn--danger:hover {
  background: rgba(239, 68, 68, 0.08);
}

/* Overlay */
.exams-page__overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

/* Confirm Dialog */
.exams-page__confirm-dialog {
  background: #fff;
  border-radius: 12px;
  padding: 28px;
  width: 400px;
  max-width: 90vw;
}

.exams-page__confirm-title {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 12px;
}

.exams-page__confirm-text {
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
  margin: 0 0 24px;
}

.exams-page__confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.exams-page__confirm-cancel {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  padding: 8px 18px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.exams-page__confirm-cancel:hover {
  background: #e2e8f0;
}

.exams-page__confirm-delete {
  background: #ef4444;
  color: #fff;
  border: none;
  border-radius: 7px;
  padding: 8px 18px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.exams-page__confirm-delete:hover {
  background: #dc2626;
}

/* Modal */
.exams-page__modal {
  background: #fff;
  border-radius: 14px;
  padding: 32px;
  width: 600px;
  max-width: 90vw;
  max-height: 85vh;
  overflow-y: auto;
}

.exams-page__modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 24px;
}

.exams-page__form-group {
  margin-bottom: 18px;
}

.exams-page__form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.exams-page__form-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 6px;
}

.exams-page__form-input {
  width: 100%;
  padding: 9px 12px;
  font-size: 13px;
  color: #1e293b;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  background: #fff;
  box-sizing: border-box;
  transition: border-color 0.15s ease;
}

.exams-page__form-input:focus {
  outline: none;
  border-color: #4a6cf7;
  box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.1);
}

.exams-page__form-textarea {
  width: 100%;
  padding: 9px 12px;
  font-size: 13px;
  color: #1e293b;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  background: #fff;
  resize: vertical;
  box-sizing: border-box;
  font-family: inherit;
  transition: border-color 0.15s ease;
}

.exams-page__form-textarea:focus {
  outline: none;
  border-color: #4a6cf7;
  box-shadow: 0 0 0 3px rgba(74, 108, 247, 0.1);
}

.exams-page__challenge-select {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.exams-page__challenge-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease;
  font-size: 13px;
}

.exams-page__challenge-option:hover {
  border-color: #4a6cf7;
}

.exams-page__challenge-option--selected {
  border-color: #4a6cf7;
  background: rgba(74, 108, 247, 0.06);
}

.exams-page__challenge-checkbox {
  accent-color: #4a6cf7;
}

.exams-page__challenge-tag {
  font-weight: 500;
  color: #334155;
}

.exams-page__challenge-difficulty {
  font-size: 11px;
  color: #94a3b8;
  background: #f1f5f9;
  padding: 1px 6px;
  border-radius: 3px;
}

.exams-page__anti-cheat {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.exams-page__checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #334155;
  cursor: pointer;
}

.exams-page__checkbox-label input[type="checkbox"] {
  accent-color: #4a6cf7;
  width: 16px;
  height: 16px;
}

.exams-page__modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid #f1f5f9;
}

.exams-page__modal-cancel {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  padding: 9px 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.exams-page__modal-cancel:hover {
  background: #e2e8f0;
}

.exams-page__modal-draft {
  background: transparent;
  color: #64748b;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  padding: 9px 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.exams-page__modal-draft:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.exams-page__modal-publish {
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff;
  border: none;
  border-radius: 7px;
  padding: 9px 20px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.exams-page__modal-publish:hover {
  opacity: 0.92;
}

/* Detail Modal */
.exams-page__detail-modal {
  background: #fff;
  border-radius: 14px;
  width: 520px;
  max-width: 90vw;
  overflow: hidden;
}

.exams-page__detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 28px 0;
}

.exams-page__detail-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.exams-page__detail-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color 0.15s;
}

.exams-page__detail-close:hover {
  color: #475569;
}

.exams-page__detail-body {
  padding: 20px 28px;
}

.exams-page__detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.exams-page__detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.exams-page__detail-label {
  font-size: 12px;
  font-weight: 500;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.exams-page__detail-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.exams-page__detail-value--mono {
  font-family: Consolas, Monaco, monospace;
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
}

.exams-page__detail-value--passrate {
  font-size: 16px;
}

.exams-page__detail-footer {
  display: flex;
  justify-content: flex-end;
  padding: 0 28px 24px;
}

.exams-page__detail-btn {
  background: #4a6cf7;
  color: #fff;
  border: none;
  border-radius: 7px;
  padding: 9px 24px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}

.exams-page__detail-btn:hover {
  opacity: 0.9;
}
</style>
