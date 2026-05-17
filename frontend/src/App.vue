<template>
  <div id="app">
    <!-- NavBar (always visible) -->
    <NavBar
      :loggedIn="loggedIn"
      :username="username"
      @login-click="showAuthModal = 'login'"
      @register-click="showAuthModal = 'register'"
      @logout="logout"
      @home="goHome"
    />

    <!-- Exam View -->
    <Exam v-if="currentExam" :article="currentExam" @finish="handleExamFinish" />

    <!-- Main View -->
    <template v-else>
      <div class="main-content">
        <!-- Hero -->
        <div class="hero">
          <h1 class="hero-title">在线编码考核</h1>
          <p class="hero-subtitle">选择一个题目，进入在线编程环境完成考核</p>
        </div>

        <!-- Article Grid -->
        <div class="article-grid">
          <div v-if="loadingArticles" class="state-msg">加载中...</div>
          <div v-else-if="articles.length === 0" class="state-msg">暂无题目</div>
          <template v-else>
            <ArticleCard
              v-for="article in articles"
              :key="article.filename"
              :article="article"
              @select="openSidebar"
            />
          </template>
        </div>
      </div>
    </template>

    <!-- Sidebar -->
    <ArticleSidebar
      v-if="selectedArticle"
      :article="selectedArticle"
      @close="selectedArticle = null"
      @enter-exam="handleEnterExam"
    />

    <!-- Auth Modal -->
    <AuthModal
      v-if="showAuthModal"
      :initialMode="showAuthModal"
      @login="handleLogin"
      @close="showAuthModal = null"
    />

    <!-- Auth Guard (未登录时拦截) -->
    <div v-if="showAuthGuard" class="modal-overlay" @click.self="showAuthGuard = false">
      <div class="guard-panel">
        <div class="guard-icon">🔐</div>
        <h3 class="guard-title">需要登录</h3>
        <p class="guard-text">请先登录或注册账号后再开始考试</p>
        <button class="btn-guard-login" @click="showAuthGuard = false; showAuthModal = 'login'">去登录</button>
        <button class="btn-guard-cancel" @click="showAuthGuard = false">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import NavBar from './NavBar.vue'
import ArticleCard from './ArticleCard.vue'
import ArticleSidebar from './ArticleSidebar.vue'
import AuthModal from './AuthModal.vue'
import Exam from './Exam.vue'

const API_BASE = 'http://localhost:8000'

// Auth state
const loggedIn = ref(false)
const username = ref('')

// Articles
const articles = ref([])
const loadingArticles = ref(false)
const selectedArticle = ref(null)
const currentExam = ref(null)

// Modal state
const showAuthModal = ref(null)   // null, 'login', 'register'
const showAuthGuard = ref(false)

const handleLogin = (user) => {
  username.value = user.name
  loggedIn.value = true
  showAuthModal.value = null
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  loggedIn.value = false
  username.value = ''
}

const goHome = () => {
  currentExam.value = null
  selectedArticle.value = null
}

const loadArticles = async () => {
  loadingArticles.value = true
  try {
    const res = await fetch(`${API_BASE}/articles`)
    if (res.ok) {
      articles.value = await res.json()
    }
  } catch (e) {
    console.error('Failed to load articles:', e)
  } finally {
    loadingArticles.value = false
  }
}

const openSidebar = (article) => {
  selectedArticle.value = article
}

const handleEnterExam = (article) => {
  selectedArticle.value = null
  if (!loggedIn.value) {
    showAuthGuard.value = true
    return
  }
  currentExam.value = article
}

const handleExamFinish = () => {
  currentExam.value = null
}

onMounted(async () => {
  const savedToken = localStorage.getItem('token')
  const savedUser = localStorage.getItem('user')
  if (savedToken && savedUser) {
    const user = JSON.parse(savedUser)
    username.value = user.name
    loggedIn.value = true
  }
  await loadArticles()
})
</script>

<style scoped>
.main-content {
  max-width: 960px;
  margin: 0 auto;
  padding: 48px 32px;
}

.hero {
  text-align: center;
  margin-bottom: 40px;
}

.hero-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px;
}

.hero-subtitle {
  font-size: 15px;
  color: #64748b;
  margin: 0;
}

.article-grid {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  justify-content: center;
}

.state-msg {
  color: #94a3b8;
  text-align: center;
  padding: 60px 20px;
  font-size: 14px;
}

/* Auth Guard */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 300;
  display: flex;
  align-items: center;
  justify-content: center;
}

.guard-panel {
  width: 360px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(24px);
  border-radius: 20px;
  padding: 36px 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.6);
  text-align: center;
  animation: scaleIn 0.2s ease;
}

@keyframes scaleIn {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.guard-icon {
  font-size: 42px;
  margin-bottom: 12px;
}

.guard-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px;
}

.guard-text {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 24px;
  line-height: 1.5;
}

.btn-guard-login {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 8px;
}
.btn-guard-login:hover {
  opacity: 0.9;
}

.btn-guard-cancel {
  width: 100%;
  padding: 12px;
  background: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  color: #64748b;
  cursor: pointer;
}
.btn-guard-cancel:hover {
  background: #f8fafc;
}
</style>
