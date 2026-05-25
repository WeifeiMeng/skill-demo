<template>
  <div class="home">
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ArticleCard from './ArticleCard.vue'
import ArticleSidebar from './ArticleSidebar.vue'

const router = useRouter()
const API_BASE = 'http://localhost:8000'

const articles = ref([])
const loadingArticles = ref(false)
const selectedArticle = ref(null)

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
  router.push({ name: 'exam', params: { filename: article.filename } })
}

onMounted(loadArticles)
</script>

<style scoped>
.home {
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
</style>
