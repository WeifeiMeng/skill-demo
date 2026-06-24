<template>
  <div class="home">
    <!-- Stat Cards Row -->
    <div class="stats-row">
      <StatCard label="总挑战数" :value="computedStats.total" color="blue" />
      <StatCard label="进行中" :value="computedStats.inProgress" color="amber" />
      <StatCard label="已完成" :value="computedStats.completed" color="green" />
      <StatCard label="AI评分平均" :value="computedStats.avgScore + '%'" color="blue" />
    </div>

    <!-- Filter Row -->
    <div class="filter-row">
      <div class="filter-group">
        <span class="filter-label">难度：</span>
        <FilterChip
          v-for="d in difficultyOptions"
          :key="d.value"
          :label="d.label"
          :modelValue="activeDifficulty === d.value"
          @update:modelValue="setDifficulty(d.value)"
        />
      </div>
      <div class="filter-group">
        <span class="filter-label">标签：</span>
        <FilterChip
          v-for="t in tagOptions"
          :key="t"
          :label="t"
          :modelValue="activeTags.includes(t)"
          @update:modelValue="toggleTag(t)"
        />
      </div>
      <input
        v-model="searchQuery"
        type="text"
        class="search-input"
        placeholder="搜索题目..."
      />
    </div>

    <!-- Main Content: Challenge Grid + Activity Panel -->
    <div class="main-content">
      <div class="challenge-area">
        <div v-if="loadingChallenges" class="state-msg">加载中...</div>
        <div v-else-if="filteredChallenges.length === 0" class="state-msg">暂无匹配题目</div>
        <div v-else class="challenge-grid">
          <div
            v-for="challenge in filteredChallenges"
            :key="challenge.filename"
            class="challenge-card"
            @click="openSidebar(challenge)"
          >
            <div class="card-header">
              <span class="card-icon">{{ challenge.icon }}</span>
              <StatusBadge :label="difficultyLabel(challenge.difficulty)" :variant="challenge.difficulty" />
            </div>
            <h3 class="card-title">{{ challenge.title }}</h3>
            <p class="card-filename">{{ challenge.filename }}</p>
            <div class="card-stats">
              <span class="card-stat">通过率: {{ challenge.passRate }}%</span>
              <span class="card-stat">{{ challenge.attemptCount }}人尝试</span>
            </div>
            <div class="card-tags">
              <span v-for="tag in challenge.tags" :key="tag" class="card-tag-pill">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Activities Panel -->
      <div class="activities-panel">
        <h3 class="panel-title">最近动态</h3>
        <div v-if="!activities.length" class="panel-empty">暂无动态</div>
        <div
          v-for="act in activities"
          :key="act.id || act.title"
          class="activity-item"
        >
          <span class="act-icon">{{ activityIcon(act.type) }}</span>
          <div class="act-content">
            <div class="act-title">{{ act.title || act.challengeName }}</div>
            <div class="act-meta">
              <span>{{ act.time }}</span>
              <span v-if="act.result" class="act-result">{{ act.result }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Sidebar -->
    <ArticleSidebar
      v-if="selectedArticle"
      :article="selectedArticle"
      @close="selectedArticle = null"
      @enter-exam="handleEnterExam"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ArticleSidebar from './ArticleSidebar.vue'
import StatCard from './components/StatCard.vue'
import FilterChip from './components/FilterChip.vue'
import StatusBadge from './components/StatusBadge.vue'
import { fetchChallenges, fetchUserActivities } from './data/api.js'

const router = useRouter()

// --- State ---
const challenges = ref([])
const activities = ref([])
const loadingChallenges = ref(false)
const selectedArticle = ref(null)
const searchQuery = ref('')
const activeDifficulty = ref('all')
const activeTags = ref([])

// --- Options ---
const difficultyOptions = [
  { label: '全部', value: 'all' },
  { label: '简单', value: 'easy' },
  { label: '中等', value: 'medium' },
  { label: '困难', value: 'hard' }
]

const tagOptions = computed(() => {
  const tagSet = new Set()
  challenges.value.forEach(c => {
    (c.tags || []).forEach(t => tagSet.add(t))
  })
  return Array.from(tagSet).sort()
})

// --- Filter Logic ---
const filteredChallenges = computed(() => {
  let result = challenges.value

  // Difficulty filter
  if (activeDifficulty.value !== 'all') {
    result = result.filter(c => c.difficulty === activeDifficulty.value)
  }

  // Tag filter
  if (activeTags.value.length > 0) {
    result = result.filter(c =>
      (c.tags || []).some(t => activeTags.value.includes(t))
    )
  }

  // Search filter
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    result = result.filter(c => c.title.toLowerCase().includes(q))
  }

  return result
})

// --- Computed Stats ---
const computedStats = computed(() => {
  let data = filteredChallenges.value
  if (data.length === 0) data = challenges.value
  const total = data.length
  const inProgress = data.filter(c => c.status === 'attempted' || c.status === 'new').length
  const completed = data.filter(c => c.status === 'solved').length
  const avgScore = data.length > 0
    ? Math.round(data.reduce((sum, c) => sum + (c.passRate || 0), 0) / data.length)
    : 0
  return { total, inProgress, completed, avgScore }
})

// --- Methods ---
function setDifficulty(value) {
  activeDifficulty.value = activeDifficulty.value === value ? 'all' : value
}

function toggleTag(tag) {
  const idx = activeTags.value.indexOf(tag)
  if (idx === -1) {
    activeTags.value.push(tag)
  } else {
    activeTags.value.splice(idx, 1)
  }
}

function difficultyLabel(d) {
  const map = { easy: '简单', medium: '中等', hard: '困难' }
  return map[d] || d
}

function activityIcon(type) {
  const map = { pass: '✅', fail: '❌', start: '▶️' }
  return map[type] || '•'
}

function openSidebar(article) {
  selectedArticle.value = article
}

function handleEnterExam(article) {
  selectedArticle.value = null
  router.push({ name: 'exam', params: { filename: article.filename } })
}

// --- Data Loading ---
onMounted(async () => {
  loadingChallenges.value = true
  try {
    const [clist, alist] = await Promise.all([
      fetchChallenges(),
      fetchUserActivities()
    ])
    challenges.value = clist
    activities.value = alist
  } catch (e) {
    console.error('Failed to load data:', e)
  } finally {
    loadingChallenges.value = false
  }
})
</script>

<style scoped>
.home {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 32px 60px;
}

/* --- Stat Cards --- */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 28px;
}

/* --- Filter Row --- */
.filter-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px 12px;
  margin-bottom: 28px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  white-space: nowrap;
}

.search-input {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 8px 14px;
  font-size: 13px;
  color: #1e293b;
  outline: none;
  transition: border-color 0.15s;
  width: 180px;
  margin-left: auto;
}
.search-input::placeholder {
  color: #94a3b8;
}
.search-input:focus {
  border-color: #4a6cf7;
}

/* --- Main Content Layout --- */
.main-content {
  display: flex;
  gap: 28px;
  align-items: flex-start;
}

.challenge-area {
  flex: 1;
  min-width: 0;
}

/* --- Challenge Grid --- */
.challenge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 18px;
}

.challenge-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.challenge-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  border-color: #4a6cf7;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-icon {
  font-size: 28px;
  line-height: 1;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  line-height: 1.3;
}

.card-filename {
  font-size: 12px;
  color: #94a3b8;
  margin: 0;
  font-family: Consolas, Monaco, monospace;
  word-break: break-all;
}

.card-stats {
  display: flex;
  gap: 16px;
}

.card-stat {
  font-size: 12px;
  color: #64748b;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: auto;
}

.card-tag-pill {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  background: #f1f5f9;
  color: #64748b;
  font-weight: 500;
}

/* --- Activities Panel --- */
.activities-panel {
  width: 280px;
  flex-shrink: 0;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  position: sticky;
  top: 20px;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}

.panel-empty {
  color: #94a3b8;
  font-size: 13px;
  text-align: center;
  padding: 24px 0;
}

.activity-item {
  display: flex;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #f1f5f9;
}
.activity-item:last-child {
  border-bottom: none;
}

.act-icon {
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 2px;
}

.act-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.act-title {
  font-size: 13px;
  font-weight: 500;
  color: #334155;
  line-height: 1.4;
}

.act-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #94a3b8;
}

.act-result {
  color: #64748b;
}

/* --- State Messages --- */
.state-msg {
  color: #94a3b8;
  text-align: center;
  padding: 60px 20px;
  font-size: 14px;
}

/* --- Responsive: stack on narrow screens --- */
@media (max-width: 900px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .main-content {
    flex-direction: column;
  }
  .activities-panel {
    width: 100%;
    position: static;
  }
}
</style>
