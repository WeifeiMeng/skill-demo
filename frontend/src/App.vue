<template>
  <div id="app">
    <!-- Login View -->
    <Login v-if="!loggedIn" @login="handleLogin" />

    <!-- Exam View -->
    <Exam v-else-if="currentExam" :article="currentExam" @finish="handleExamFinish" />

    <!-- Main View -->
    <template v-else>
      <div id="topbar">
        <span class="user-info">{{ username }}</span>
        <button @click="logout" class="logout-btn">Logout</button>
      </div>

      <div id="main-content">
        <!-- Articles Panel -->
        <div id="article-grid">
          <h3>题目列表</h3>
          <div v-if="loadingArticles" class="loading">Loading articles...</div>
          <div v-else-if="articles.length === 0" class="no-articles">
            暂无题目
          </div>
          <div v-else id="article-list">
            <div
              v-for="article in articles"
              :key="article.filename"
              class="article-card"
              @click="launchEnv(article)"
            >
              <div class="article-icon">📄</div>
              <div class="article-title">{{ article.title }}</div>
              <div class="article-filename">{{ article.filename }}</div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Login from './Login.vue'
import Exam from './Exam.vue'

const API_BASE = 'http://localhost:8000'

// Auth state
const loggedIn = ref(false)
const username = ref('')
const token = ref('')

// Articles
const articles = ref([])
const loadingArticles = ref(false)
const currentExam = ref(null)

const handleLogin = (user) => {
  username.value = user.name
  loggedIn.value = true
  loadArticles()
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  loggedIn.value = false
  username.value = ''
  token.value = ''
}

const getHeaders = () => {
  const t = localStorage.getItem('token')
  if (t) {
    return { 'Authorization': `Bearer ${t}` }
  }
  return {}
}

const loadArticles = async () => {
  loadingArticles.value = true
  try {
    const res = await fetch(`${API_BASE}/articles`, { headers: getHeaders() })
    articles.value = await res.json()
  } catch (e) {
    console.error('Failed to load articles:', e)
  } finally {
    loadingArticles.value = false
  }
}

const handleExamFinish = () => {
  currentExam.value = null
}

const launchEnv = (article) => {
  currentExam.value = article
}

onMounted(() => {
  // 检查是否有保存的登录状态
  const savedToken = localStorage.getItem('token')
  const savedUser = localStorage.getItem('user')
  if (savedToken && savedUser) {
    token.value = savedToken
    const user = JSON.parse(savedUser)
    username.value = user.name
    loggedIn.value = true
    loadArticles()
  }
})

</script>

<style scoped>
#topbar {
  display: flex;
  gap: 10px;
  padding: 12px 20px;
  background: #16213e;
  border-bottom: 1px solid #0f3460;
}

#topbar button {
  padding: 8px 16px;
  background: #0f3460;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

#topbar button:hover:not(:disabled) {
  background: #e94560;
}

#topbar button:disabled {
  background: #333;
  cursor: not-allowed;
}

.user-info {
  margin-right: auto;
  color: #e94560;
  font-weight: bold;
  padding: 8px 0;
}

.logout-btn {
  background: #6c3b3b !important;
}

#main-content {
  height: calc(100vh - 57px);
  background: #1a1a2e;
  overflow-y: auto;
  padding: 20px;
}

#article-grid h3 {
  color: #e94560;
  margin: 0 0 20px 0;
  font-size: 18px;
}

.loading, .no-articles {
  color: #6c6c6c;
  text-align: center;
  padding: 40px;
  font-size: 14px;
}

#article-list {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.article-card {
  flex: 0 0 200px;
  background: #16213e;
  border-radius: 12px;
  padding: 24px 16px;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.article-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(233, 69, 96, 0.2);
}

.article-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.article-title {
  color: #fff;
  font-weight: bold;
  font-size: 15px;
  margin-bottom: 4px;
  word-break: break-word;
}

.article-filename {
  color: #6c6c6c;
  font-size: 11px;
  margin-top: 4px;
}

</style>
