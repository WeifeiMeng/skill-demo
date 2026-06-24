<template>
  <div class="solutions-page">
    <div class="page-header">
      <h1 class="page-title">题解广场</h1>
      <p class="page-subtitle">精选社区优质题解，从他人的思路中汲取灵感</p>
    </div>

    <div class="filter-bar">
      <div class="filter-chips">
        <FilterChip v-model="filterFeatured" label="精选" />
        <FilterChip v-model="filterNewest" label="最新" />
        <FilterChip v-model="filterHottest" label="最热" />
      </div>
      <div class="search-box">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
          <circle cx="7" cy="7" r="5.5" stroke="#94a3b8" stroke-width="1.5" />
          <path d="M11 11l3.5 3.5" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round" />
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="搜索题解..."
        />
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="filteredSolutions.length === 0" class="empty-state">
      <p>没有找到匹配的题解</p>
    </div>

    <div v-else class="solutions-grid">
      <div
        v-for="sol in filteredSolutions"
        :key="sol.id"
        class="solution-card"
        :class="{
          'solution-card--featured': sol.featured,
          'solution-card--easy': sol.difficulty === 'easy',
          'solution-card--medium': sol.difficulty === 'medium',
          'solution-card--hard': sol.difficulty === 'hard',
        }"
        @click="openDetail(sol)"
      >
        <div class="card-header">
          <span class="card-challenge-name">{{ sol.problem }}</span>
          <StatusBadge :label="difficultyLabel(sol.difficulty)" :variant="sol.difficulty" />
        </div>
        <h3 class="card-title">{{ sol.title }}</h3>
        <p class="card-summary">{{ sol.summary }}</p>
        <div class="card-code-preview">
          <pre class="code-snippet">{{ sol.codePreview }}</pre>
        </div>
        <div class="card-tags" v-if="sol.tags && sol.tags.length">
          <span v-for="tag in sol.tags" :key="tag" class="card-tag">{{ tag }}</span>
        </div>
        <div class="card-footer">
          <div class="card-author">
            <span class="author-avatar">{{ (sol.author.name || '?')[0] }}</span>
            <span class="author-name">{{ sol.author.name }}</span>
          </div>
          <div class="card-stats">
            <span class="stat-item">❤️ {{ sol.likes }}</span>
            <span class="stat-item">⭐ {{ sol.stars }}</span>
            <span class="stat-item">💬 {{ sol.comments }}</span>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="selectedSolution" class="modal-overlay" @click.self="closeDetail">
        <div class="modal-card">
          <button class="modal-close" @click="closeDetail">&times;</button>
          <div class="modal-header">
            <h2 class="modal-title">{{ selectedSolution.title }}</h2>
            <StatusBadge :label="difficultyLabel(selectedSolution.difficulty)" :variant="selectedSolution.difficulty" />
          </div>

          <div class="modal-section">
            <h3 class="modal-section-title">解题思路</h3>
            <p class="modal-text">{{ selectedSolution.fullContent?.approach || '暂无解题思路' }}</p>
          </div>

          <div class="modal-section">
            <h3 class="modal-section-title">完整代码</h3>
            <CodeBlock :code="selectedSolution.fullContent?.fullCode || '// 暂无代码'" />
          </div>

          <div class="modal-section">
            <h3 class="modal-section-title">复杂度分析</h3>
            <div class="complexity-cards">
              <div class="complexity-card">
                <span class="complexity-label">时间复杂度</span>
                <span class="complexity-value">{{ selectedSolution.fullContent?.timeComplexity || '-' }}</span>
              </div>
              <div class="complexity-card">
                <span class="complexity-label">空间复杂度</span>
                <span class="complexity-value">{{ selectedSolution.fullContent?.spaceComplexity || '-' }}</span>
              </div>
            </div>
          </div>

          <div class="modal-section" v-if="selectedSolution.fullContent?.pitfalls?.length">
            <h3 class="modal-section-title">踩坑记录</h3>
            <ol class="pitfall-list">
              <li v-for="(item, idx) in selectedSolution.fullContent.pitfalls" :key="idx" class="pitfall-item">
                {{ item }}
              </li>
            </ol>
          </div>

          <div class="modal-actions">
            <button class="action-btn">❤️ 点赞 ({{ selectedSolution.likes }})</button>
            <button class="action-btn">⭐ 收藏 ({{ selectedSolution.stars }})</button>
            <button class="action-btn">💬 评论 ({{ selectedSolution.comments }})</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import StatusBadge from './components/StatusBadge.vue'
import FilterChip from './components/FilterChip.vue'
import CodeBlock from './components/CodeBlock.vue'
import { fetchSolutions } from './data/api.js'

const solutions = ref([])
const loading = ref(true)
const selectedSolution = ref(null)
const searchQuery = ref('')
const filterFeatured = ref(false)
const filterNewest = ref(false)
const filterHottest = ref(false)

const filteredSolutions = computed(() => {
  let result = [...solutions.value]

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    result = result.filter(s =>
      s.title.toLowerCase().includes(q) ||
      s.summary.toLowerCase().includes(q) ||
      (s.tags && s.tags.some(t => t.toLowerCase().includes(q))) ||
      (s.author && s.author.name.toLowerCase().includes(q))
    )
  }

  if (filterFeatured.value) {
    result = result.filter(s => s.featured)
  }
  if (filterNewest.value) {
    result = result.filter(s => s.featured)
  }
  if (filterHottest.value) {
    result = result.sort((a, b) => (b.likes || 0) - (a.likes || 0))
  }

  return result
})

function difficultyLabel(d) {
  const map = { easy: '简单', medium: '中等', hard: '困难' }
  return map[d] || d
}

function openDetail(sol) {
  selectedSolution.value = sol
  document.body.style.overflow = 'hidden'
}

function closeDetail() {
  selectedSolution.value = null
  document.body.style.overflow = ''
}

onMounted(async () => {
  try {
    solutions.value = await fetchSolutions()
  } catch (_) {
    solutions.value = []
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.solutions-page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px;
}

.page-header {
  margin-bottom: 28px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 6px;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

/* Filter Bar */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-chips {
  display: flex;
  gap: 8px;
}

.search-box {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

.search-input {
  padding: 8px 14px 8px 36px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  color: #334155;
  background: #fff;
  outline: none;
  width: 220px;
  transition: border-color 0.15s;
}

.search-input::placeholder {
  color: #94a3b8;
}

.search-input:focus {
  border-color: #4a6cf7;
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

/* Grid */
.solutions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 768px) {
  .solutions-grid {
    grid-template-columns: 1fr;
  }
  .solutions-page {
    padding: 20px;
  }
}

/* Card */
.solution-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px 24px;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.15s, border-color 0.15s;
}

.solution-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

.solution-card--easy {
  border-left-color: #22c55e;
}

.solution-card--medium {
  border-left-color: #f59e0b;
}

.solution-card--hard {
  border-left-color: #ef4444;
}

.solution-card--featured {
  border: 2px solid #f59e0b;
  border-left: 4px solid #f59e0b;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.card-challenge-name {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px;
  line-height: 1.4;
}

.card-summary {
  font-size: 13px;
  color: #64748b;
  line-height: 1.6;
  margin: 0 0 14px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-code-preview {
  background: #0f172a;
  border-radius: 8px;
  padding: 12px 14px;
  height: 80px;
  overflow: hidden;
  margin-bottom: 14px;
  mask-image: linear-gradient(to bottom, black 60%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, black 60%, transparent 100%);
}

.code-snippet {
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 12px;
  color: #e2e8f0;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 14px;
}

.card-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  background: #f1f5f9;
  color: #64748b;
  font-size: 11px;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.author-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #cbd5e1;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.author-name {
  font-size: 13px;
  color: #334155;
  font-weight: 500;
}

.card-stats {
  display: flex;
  gap: 12px;
}

.stat-item {
  font-size: 13px;
  color: #94a3b8;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
}

.modal-card {
  background: #fff;
  border-radius: 16px;
  max-width: 700px;
  width: 100%;
  max-height: 80vh;
  overflow-y: auto;
  padding: 32px;
  position: relative;
}

.modal-card::-webkit-scrollbar {
  width: 6px;
}

.modal-card::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 20px;
  background: none;
  border: none;
  font-size: 24px;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-close:hover {
  color: #334155;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding-right: 30px;
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.modal-section {
  margin-bottom: 24px;
}

.modal-section-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 12px;
}

.modal-text {
  font-size: 14px;
  color: #334155;
  line-height: 1.8;
  margin: 0;
}

.complexity-cards {
  display: flex;
  gap: 16px;
}

.complexity-card {
  flex: 1;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.complexity-label {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
}

.complexity-value {
  font-size: 14px;
  color: #1e293b;
  font-weight: 600;
}

.pitfall-list {
  margin: 0;
  padding-left: 20px;
}

.pitfall-item {
  font-size: 14px;
  color: #334155;
  line-height: 1.8;
  margin-bottom: 6px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.action-btn {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  color: #334155;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.action-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}
</style>
