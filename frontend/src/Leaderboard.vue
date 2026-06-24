<template>
  <div class="leaderboard-page">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <template v-else>
      <!-- Current User Rating -->
      <div class="rating-section" v-if="currentUser">
        <RatingCard
          :rating="currentUser.rating"
          :rank="currentUser.rank"
          :total="totalEntries"
          :tier-name="currentUser.tierName"
          :tier-short="currentUser.tier"
        >
          <template #stats>
            <div class="stat-item">
              <span class="stat-label">参赛次数</span>
              <span class="stat-value">{{ currentUser.contests }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">胜率</span>
              <span class="stat-value">{{ currentUser.winRate }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">变化</span>
              <span
                class="stat-change"
                :class="currentUser.change >= 0 ? 'stat-change--up' : 'stat-change--down'"
              >
                {{ currentUser.change >= 0 ? '+' : '' }}{{ currentUser.change }}
              </span>
            </div>
          </template>
        </RatingCard>
      </div>

      <!-- Tier Legend -->
      <div class="tier-legend">
        <span
          v-for="tier in tiers"
          :key="tier.name"
          class="tier-dot"
          :style="{ background: tier.color }"
        >
          <span class="tier-name">{{ tier.name }}</span>
        </span>
      </div>

      <!-- Rating Trend Chart -->
      <div class="trend-section" v-if="ratingTrend.length">
        <h3 class="section-title">Rating 趋势</h3>
        <div class="trend-chart">
          <div
            v-for="point in normalizedTrend"
            :key="point.label"
            class="trend-bar-wrapper"
            @mouseenter="hoveredBar = point"
            @mouseleave="hoveredBar = null"
          >
            <div class="trend-bar-container">
              <div
                class="trend-bar"
                :style="{ height: point.heightPercent + '%' }"
              ></div>
            </div>
            <span class="trend-label">{{ point.label }}</span>
            <div v-if="hoveredBar === point" class="trend-tooltip">
              {{ point.value }}
            </div>
          </div>
        </div>
      </div>

      <!-- Tab Row -->
      <div class="tab-row">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ 'tab-btn--active': activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Ranking Table -->
      <div class="ranking-table-wrapper">
        <table class="ranking-table">
          <thead>
            <tr>
              <th class="col-rank">排名</th>
              <th class="col-player">选手</th>
              <th class="col-tier">段位</th>
              <th class="col-rating">Rating</th>
              <th class="col-contests">参赛</th>
              <th class="col-winrate">胜率</th>
              <th class="col-peak">峰值</th>
              <th class="col-recent">最近</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="entry in paginatedEntries"
              :key="entry.rank"
              class="ranking-row"
              :class="{ 'ranking-row--current': entry.rank === currentUser?.rank }"
            >
              <td class="col-rank">
                <span v-if="entry.rank === 1" class="medal">🥇</span>
                <span v-else-if="entry.rank === 2" class="medal">🥈</span>
                <span v-else-if="entry.rank === 3" class="medal">🥉</span>
                <span v-else class="rank-num">{{ entry.rank }}</span>
              </td>
              <td class="col-player">
                <div class="player-cell">
                  <span
                    class="player-avatar"
                    :style="{ background: avatarColor(entry.name) }"
                  >{{ (entry.name || '?')[0] }}</span>
                  <span class="player-name">{{ entry.name }}</span>
                </div>
              </td>
              <td class="col-tier">
                <span class="tier-title" :style="{ color: tierColor(entry.tier) }">
                  {{ entry.tierName }}
                </span>
              </td>
              <td class="col-rating">
                <span class="rating-value">{{ entry.rating }}</span>
                <span
                  v-if="entry.change"
                  class="rating-change"
                  :class="entry.change > 0 ? 'change--up' : 'change--down'"
                >
                  {{ entry.change > 0 ? '+' : '' }}{{ entry.change }}
                </span>
              </td>
              <td class="col-contests">{{ entry.contests }}</td>
              <td class="col-winrate">{{ entry.winRate }}%</td>
              <td class="col-peak">{{ entry.peak }}</td>
              <td class="col-recent">
                <span
                  v-for="(r, idx) in (entry.recent || []).slice(0, 5)"
                  :key="idx"
                  class="recent-chip"
                  :class="recentChipClass(r)"
                >
                  {{ r }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div class="pagination" v-if="totalPages > 1">
        <button
          class="page-btn"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          上一页
        </button>
        <button
          v-for="p in visiblePages"
          :key="p"
          class="page-num"
          :class="{ 'page-num--active': p === currentPage }"
          @click="currentPage = p"
        >
          {{ p }}
        </button>
        <button
          class="page-btn"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          下一页
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import RatingCard from './components/RatingCard.vue'
import { fetchLeaderboard, fetchRatingTrend } from './data/api.js'

const leaderboard = ref(null)
const ratingTrend = ref([])
const loading = ref(true)
const activeTab = ref('total')
const currentPage = ref(1)
const hoveredBar = ref(null)
const pageSize = 20

const tabs = [
  { key: 'total', label: '总排名' },
  { key: 'weekly', label: '周榜' },
  { key: 'monthly', label: '月榜' },
  { key: 'solved', label: '做题数' },
  { key: 'winrate', label: '胜率' },
]

const tiers = [
  { name: '传奇王者', color: '#ff6b6b' },
  { name: '钻石', color: '#4ecdc4' },
  { name: '铂金', color: '#45b7d1' },
  { name: '黄金', color: '#f9ca24' },
  { name: '白银', color: '#a0aec0' },
  { name: '青铜', color: '#ed8936' },
  { name: '黑铁', color: '#718096' },
]

const tierColorMap = {
  legend: '#ff6b6b',
  diamond: '#4ecdc4',
  platinum: '#45b7d1',
  gold: '#f9ca24',
  silver: '#a0aec0',
  bronze: '#ed8936',
  iron: '#718096',
}

function tierColor(tier) {
  return tierColorMap[tier] || '#94a3b8'
}

const avatarColors = ['#4a6cf7', '#ec4899', '#f59e0b', '#22c55e', '#a855f7', '#06b6d4', '#ef4444', '#84cc16']
function avatarColor(name) {
  let hash = 0
  for (let i = 0; i < (name || '').length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return avatarColors[Math.abs(hash) % avatarColors.length]
}

const totalEntries = computed(() => leaderboard.value?.total || 0)
const entries = computed(() => leaderboard.value?.entries || [])

const currentUser = computed(() => {
  if (!entries.value.length) return null
  return entries.value.find(e => e.name === '王五') || entries.value[0]
})

const sortedEntries = computed(() => {
  let list = [...entries.value]
  switch (activeTab.value) {
    case 'weekly':
    case 'monthly':
      // Use recent first result as proxy
      list.sort((a, b) => ((b.recent || [])[0] || 999) - ((a.recent || [])[0] || 999))
      break
    case 'solved':
      // No solved count in mock, fall back to contests
      list.sort((a, b) => b.contests - a.contests)
      break
    case 'winrate':
      list.sort((a, b) => b.winRate - a.winRate)
      break
    case 'total':
    default:
      list.sort((a, b) => a.rank - b.rank)
      break
  }
  return list
})

const totalPages = computed(() => Math.max(1, Math.ceil(sortedEntries.value.length / pageSize)))

const paginatedEntries = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return sortedEntries.value.slice(start, start + pageSize)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  let start = Math.max(1, current - 2)
  let end = Math.min(total, current + 2)
  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(total, start + 4)
    } else {
      start = Math.max(1, end - 4)
    }
  }
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

function recentChipClass(r) {
  if (r <= 3) return 'recent--gold'
  if (r <= 10) return 'recent--silver'
  if (r <= 50) return 'recent--bronze'
  return 'recent--normal'
}

const normalizedTrend = computed(() => {
  if (!ratingTrend.value.length) return []
  const values = ratingTrend.value.map(p => p.value)
  const minVal = Math.min(...values)
  const maxVal = Math.max(...values)
  const range = maxVal - minVal || 1
  return ratingTrend.value.map(p => ({
    label: p.label,
    value: p.value,
    heightPercent: ((p.value - minVal) / range) * 85 + 10,
  }))
})

onMounted(async () => {
  try {
    const [lb, trend] = await Promise.all([
      fetchLeaderboard(),
      fetchRatingTrend(),
    ])
    leaderboard.value = lb
    ratingTrend.value = trend
  } catch (_) {
    leaderboard.value = { total: 0, entries: [] }
    ratingTrend.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.leaderboard-page {
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

/* Rating Section */
.rating-section {
  margin-bottom: 28px;
}

.rating-section :deep(.stat-item) {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rating-section :deep(.stat-label) {
  color: #64748b;
}

.rating-section :deep(.stat-value) {
  color: #f1f5f9;
  font-weight: 600;
}

.rating-section :deep(.stat-change) {
  font-weight: 600;
  font-size: 13px;
}

.rating-section :deep(.stat-change--up) {
  color: #22c55e;
}

.rating-section :deep(.stat-change--down) {
  color: #ef4444;
}

/* Tier Legend */
.tier-legend {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}

.tier-dot {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  position: relative;
}

.tier-name {
  position: absolute;
  left: 20px;
  font-size: 12px;
  color: #64748b;
  white-space: nowrap;
  font-weight: 500;
}

/* Trend Section */
.trend-section {
  margin-bottom: 28px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px;
}

.trend-chart {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  height: 160px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px 24px 8px;
  overflow-x: auto;
}

.trend-bar-wrapper {
  flex: 1;
  min-width: 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.trend-bar-container {
  flex: 1;
  width: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.trend-bar {
  width: 60%;
  border-radius: 4px 4px 0 0;
  background: linear-gradient(to top, #4a6cf7, #6a3de8);
  min-height: 4px;
  transition: width 0.2s;
}

.trend-bar-wrapper:hover .trend-bar {
  width: 80%;
  opacity: 0.8;
}

.trend-label {
  font-size: 10px;
  color: #94a3b8;
  margin-top: 6px;
  white-space: nowrap;
}

.trend-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #0f172a;
  color: #f1f5f9;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  white-space: nowrap;
  margin-bottom: 4px;
  pointer-events: none;
}

/* Tab Row */
.tab-row {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 7px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  background: #fff;
  color: #64748b;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.tab-btn:hover {
  border-color: #cbd5e1;
}

.tab-btn--active {
  background: rgba(74, 108, 247, 0.08);
  border-color: #4a6cf7;
  color: #4a6cf7;
  font-weight: 500;
}

/* Ranking Table */
.ranking-table-wrapper {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
}

.ranking-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.ranking-table thead {
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.ranking-table th {
  padding: 12px 14px;
  text-align: left;
  font-weight: 600;
  color: #64748b;
  font-size: 12px;
  white-space: nowrap;
}

.ranking-table td {
  padding: 12px 14px;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.ranking-row:last-child td {
  border-bottom: none;
}

.ranking-row:hover {
  background: #f8fafc;
}

.ranking-row--current {
  background: rgba(74, 108, 247, 0.04);
}

.ranking-row--current:hover {
  background: rgba(74, 108, 247, 0.07);
}

.col-rank {
  width: 60px;
  text-align: center;
}

.medal {
  font-size: 16px;
}

.rank-num {
  color: #64748b;
  font-weight: 500;
}

.player-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.player-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.player-name {
  font-weight: 500;
  color: #1e293b;
}

.tier-title {
  font-size: 12px;
  font-weight: 600;
}

.rating-value {
  font-weight: 600;
  color: #1e293b;
}

.rating-change {
  margin-left: 6px;
  font-size: 12px;
  font-weight: 600;
}

.change--up {
  color: #22c55e;
}

.change--down {
  color: #ef4444;
}

.col-contests,
.col-winrate,
.col-peak {
  color: #334155;
}

.recent-chip {
  display: inline-block;
  font-size: 10px;
  font-weight: 600;
  padding: 1px 5px;
  border-radius: 3px;
  margin-right: 3px;
}

.recent--gold {
  background: #fef3c7;
  color: #b45309;
}

.recent--silver {
  background: #f1f5f9;
  color: #475569;
}

.recent--bronze {
  background: #fef2f2;
  color: #b45309;
}

.recent--normal {
  background: #f8fafc;
  color: #94a3b8;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.page-btn {
  padding: 6px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #fff;
  color: #334155;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.page-btn:hover:not(:disabled) {
  border-color: #cbd5e1;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-num {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: #fff;
  color: #334155;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.page-num:hover {
  border-color: #cbd5e1;
}

.page-num--active {
  background: #4a6cf7;
  border-color: #4a6cf7;
  color: #fff;
}

/* Responsive */
@media (max-width: 768px) {
  .leaderboard-page {
    padding: 20px;
  }
  .ranking-table-wrapper {
    overflow-x: auto;
  }
  .ranking-table {
    min-width: 700px;
  }
}
</style>
