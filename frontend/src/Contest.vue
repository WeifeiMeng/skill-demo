<template>
  <div class="contest-page">
    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <template v-else-if="contestData">
      <!-- Hero Banner -->
      <div class="hero-banner">
        <div class="hero-content">
          <h1 class="hero-title">{{ contestData.title }}</h1>
          <div class="hero-theme" v-if="contestData.theme">{{ contestData.theme }}</div>
          <div class="countdown-row">
            <div class="countdown-unit">
              <span class="countdown-value">{{ countdown.days }}</span>
              <span class="countdown-label">天</span>
            </div>
            <span class="countdown-sep">:</span>
            <div class="countdown-unit">
              <span class="countdown-value">{{ countdown.hours }}</span>
              <span class="countdown-label">时</span>
            </div>
            <span class="countdown-sep">:</span>
            <div class="countdown-unit">
              <span class="countdown-value">{{ countdown.minutes }}</span>
              <span class="countdown-label">分</span>
            </div>
            <span class="countdown-sep">:</span>
            <div class="countdown-unit">
              <span class="countdown-value">{{ countdown.seconds }}</span>
              <span class="countdown-label">秒</span>
            </div>
          </div>
          <div class="hero-stats">
            <div class="hero-stat">
              <span class="hero-stat-value">{{ contestData.registered }}</span>
              <span class="hero-stat-label">已报名</span>
            </div>
            <div class="hero-stat">
              <span class="hero-stat-value">{{ contestData.problemCount }}</span>
              <span class="hero-stat-label">题目数</span>
            </div>
            <div class="hero-stat">
              <span class="hero-stat-value">{{ contestData.pointsReward }}</span>
              <span class="hero-stat-label">总积分</span>
            </div>
            <div class="hero-stat">
              <span class="hero-stat-value">{{ contestData.completionRate }}%</span>
              <span class="hero-stat-label">完成率</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Two-column layout -->
      <div class="contest-body">
        <div class="contest-left">
          <h2 class="section-title">题目列表</h2>
          <div class="problem-list">
            <div
              v-for="(p, idx) in contestData.problems"
              :key="idx"
              class="problem-row"
            >
              <span
                class="problem-status-bar"
                :class="{
                  'status--solved': p.status === 'solved',
                  'status--attempted': p.status === 'attempted',
                  'status--new': p.status === 'new',
                }"
              ></span>
              <div class="problem-info">
                <span class="problem-name">{{ p.name }}</span>
                <span class="problem-tag" v-if="p.tag">{{ p.tag }}</span>
              </div>
              <StatusBadge :label="problemStatusLabel(p.status)" :variant="p.status" />
            </div>
          </div>
        </div>

        <div class="contest-right">
          <h2 class="section-title">实时排行 TOP 5</h2>
          <div class="ranking-table">
            <div
              v-for="r in contestData.topRank"
              :key="r.rank"
              class="ranking-row"
            >
              <span class="rank-badge" :class="'rank--' + r.rank">
                {{ r.rank }}
              </span>
              <span class="rank-name">{{ r.name }}</span>
              <span class="rank-score">{{ r.rating }}</span>
              <span class="rank-solved">{{ r.solved }}/{{ contestData.problemCount }} 题</span>
            </div>
          </div>
        </div>
      </div>

      <!-- History -->
      <div class="history-section">
        <h2 class="section-title">历史竞赛</h2>
        <div class="history-grid" v-if="contestData.history && contestData.history.length">
          <div
            v-for="(h, idx) in contestData.history"
            :key="idx"
            class="history-card"
          >
            <h3 class="history-name">{{ h.title }}</h3>
            <p class="history-date">{{ h.date }}</p>
            <div class="history-rank-row">
              <span class="history-rank">第 {{ h.rank }} 名</span>
            </div>
            <div class="history-rating" :class="{ 'rating--up': getRatingChange(idx) > 0, 'rating--down': getRatingChange(idx) < 0 }">
              <span v-if="getRatingChange(idx) > 0">+{{ getRatingChange(idx) }} ↑</span>
              <span v-else-if="getRatingChange(idx) < 0">{{ getRatingChange(idx) }} ↓</span>
              <span v-else>0</span>
            </div>
            <div class="history-score">
              <span class="history-score-label">Rating</span>
              <span class="history-score-value">{{ h.rating }}</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>暂无历史竞赛数据</p>
        </div>
      </div>
    </template>

    <div v-else class="empty-state">
      <p>暂无竞赛数据</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import StatusBadge from './components/StatusBadge.vue'
import { fetchContestData } from './data/api.js'

const contestData = ref(null)
const loading = ref(true)
const remainingSeconds = ref(0)
let timer = null

const countdown = computed(() => {
  const t = Math.max(0, remainingSeconds.value)
  const days = Math.floor(t / 86400)
  const hours = Math.floor((t % 86400) / 3600)
  const minutes = Math.floor((t % 3600) / 60)
  const seconds = t % 60
  return {
    days: String(days).padStart(2, '0'),
    hours: String(hours).padStart(2, '0'),
    minutes: String(minutes).padStart(2, '0'),
    seconds: String(seconds).padStart(2, '0'),
  }
})

function problemStatusLabel(status) {
  const map = { solved: '已解决', attempted: '尝试中', new: '新' }
  return map[status] || status
}

function getRatingChange(idx) {
  if (!contestData.value?.history) return 0
  const current = contestData.value.history[idx]
  const next = contestData.value.history[idx + 1]
  if (!next) return 0
  return current.rating - next.rating
}

onMounted(async () => {
  try {
    const data = await fetchContestData()
    contestData.value = data
    remainingSeconds.value = data.countdown || 0
    timer = setInterval(() => {
      if (remainingSeconds.value > 0) {
        remainingSeconds.value--
      }
    }, 1000)
  } catch (_) {
    contestData.value = null
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.contest-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px;
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80px 0;
  color: #94a3b8;
  font-size: 14px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e2e8f0;
  border-top-color: #4a6cf7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 12px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 80px 0;
  color: #94a3b8;
  font-size: 14px;
}

/* Hero Banner */
.hero-banner {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1a1a2e 100%);
  border-radius: 12px;
  padding: 48px 32px;
  margin-bottom: 32px;
}

.hero-content {
  text-align: center;
}

.hero-title {
  font-size: 28px;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 8px;
}

.hero-theme {
  font-size: 15px;
  color: #64748b;
  margin-bottom: 28px;
}

.countdown-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 32px;
}

.countdown-unit {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 52px;
}

.countdown-value {
  font-size: 22px;
  font-weight: 700;
  color: #f1f5f9;
  line-height: 1.1;
}

.countdown-label {
  font-size: 11px;
  color: #64748b;
  margin-top: 2px;
}

.countdown-sep {
  font-size: 22px;
  font-weight: 700;
  color: #64748b;
  padding-bottom: 14px;
}

.hero-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 48px;
  flex-wrap: wrap;
}

.hero-stat {
  text-align: center;
}

.hero-stat-value {
  display: block;
  font-size: 22px;
  font-weight: 700;
  color: #f1f5f9;
}

.hero-stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

/* Contest Body */
.contest-body {
  display: flex;
  gap: 24px;
  margin-bottom: 48px;
}

.contest-left {
  flex: 2;
  min-width: 0;
}

.contest-right {
  flex: 1;
  min-width: 0;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px;
}

/* Problem List */
.problem-list {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.problem-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid #f1f5f9;
  transition: background 0.15s;
}

.problem-row:last-child {
  border-bottom: none;
}

.problem-row:hover {
  background: #f8fafc;
}

.problem-status-bar {
  width: 4px;
  height: 32px;
  border-radius: 2px;
  background: #cbd5e1;
  flex-shrink: 0;
}

.problem-status-bar.status--solved {
  background: #22c55e;
}

.problem-status-bar.status--attempted {
  background: #f59e0b;
}

.problem-status-bar.status--new {
  background: #cbd5e1;
}

.problem-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.problem-name {
  font-size: 14px;
  color: #1e293b;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.problem-tag {
  font-size: 11px;
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 4px;
  flex-shrink: 0;
}

/* Ranking Table */
.ranking-table {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.ranking-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 13px;
}

.ranking-row:last-child {
  border-bottom: none;
}

.rank-badge {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  background: #94a3b8;
  flex-shrink: 0;
}

.rank-badge.rank--1 {
  background: #f59e0b;
}

.rank-badge.rank--2 {
  background: #94a3b8;
}

.rank-badge.rank--3 {
  background: #ed8936;
}

.rank-name {
  flex: 1;
  font-weight: 500;
  color: #1e293b;
}

.rank-score {
  color: #4a6cf7;
  font-weight: 600;
}

.rank-solved {
  color: #94a3b8;
  font-size: 12px;
}

/* History */
.history-section {
  margin-bottom: 24px;
}

.history-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

@media (max-width: 768px) {
  .history-grid {
    grid-template-columns: 1fr;
  }
}

.history-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  transition: box-shadow 0.15s;
}

.history-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.history-name {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 6px;
}

.history-date {
  font-size: 13px;
  color: #94a3b8;
  margin: 0 0 14px;
}

.history-rank-row {
  margin-bottom: 8px;
}

.history-rank {
  font-size: 14px;
  color: #334155;
  font-weight: 500;
}

.history-rating {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 10px;
}

.history-rating.rating--up {
  color: #22c55e;
}

.history-rating.rating--down {
  color: #ef4444;
}

.history-score {
  display: flex;
  align-items: center;
  gap: 6px;
}

.history-score-label {
  font-size: 12px;
  color: #94a3b8;
}

.history-score-value {
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}

@media (max-width: 768px) {
  .contest-body {
    flex-direction: column;
  }
  .hero-banner {
    padding: 32px 20px;
  }
  .hero-title {
    font-size: 22px;
  }
  .hero-stats {
    gap: 24px;
  }
  .contest-page {
    padding: 20px;
  }
}
</style>
