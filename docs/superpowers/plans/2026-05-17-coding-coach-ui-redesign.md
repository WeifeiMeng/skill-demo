# Coding Coach UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform Mini CodeSandbox's frontend from dark AI theme to a light glassmorphism-style online coding exam platform "Coding Coach".

**Architecture:** Vue 3 SPA with modal-based auth (replacing separate login page), side panel for article preview, and auth gate before exam entry. Backend removes auth requirement from article listing endpoint and adds description field.

**Tech Stack:** Vue 3 + Vite (frontend), FastAPI + Docker SDK (backend), glassmorphism CSS

---

### Task 1: Backend — Remove article auth + add description field

**Files:**
- Modify: `backend/route/article.py`
- Modify: `backend/service/article_service.py`

- [ ] **Step 1: Remove auth dependency from GET /articles in route/article.py**

```python
# Before:
from route.dependencies import get_current_user
@router.get("")
def get_articles(user: User = Depends(get_current_user)):
    return list_articles()

# After:
@router.get("")
def get_articles():
    """获取所有文章（题目）列表，无需登录"""
    return list_articles()
```

Remove unused imports (`Depends`, `get_current_user`, `User`) from the file.

- [ ] **Step 2: Add description extraction and NAME_MAP update in article_service.py**

```python
# Add DESCRIPTION_MAP after NAME_MAP:
# 文件名到简介的映射
DESCRIPTION_MAP = {
    "deep-face-search.md": "给定一张模糊的人脸图片，通过多轮搜索与用户反馈确认，最终定位到具体人员档案。考察函数调用策略、搜索流程设计与 Top1 限制的解决方案。",
    "advanced-short-url.md": "用 Python 实现一个高性能短链接后端服务，支持长 URL 转短码、302 重定向跳转，以及基于滑动窗口算法的用户级限流。",
}

# Update list_articles() to include description:
def list_articles():
    result = []
    if not os.path.exists(ARTICLES_DIR):
        return result
    for fname in sorted(os.listdir(ARTICLES_DIR)):
        if not fname.endswith(".md"):
            continue
        filepath = os.path.join(ARTICLES_DIR, fname)
        title = NAME_MAP.get(fname)
        if not title:
            title = _extract_title_from_md(filepath)
        if not title:
            title = _default_title(fname)
        result.append({
            "filename": fname,
            "title": title,
            "description": DESCRIPTION_MAP.get(fname, ""),
        })
    return result
```

- [ ] **Step 3: Verify backend starts**

Run: `cd backend && uvicorn main:app --reload --port 8000`
Expected: Server starts on port 8000, `GET /articles` returns articles without auth header.

- [ ] **Step 4: Commit**

```bash
git add backend/route/article.py backend/service/article_service.py
git commit -m "feat: allow unauthenticated article list access, add description field"
```

---

### Task 2: Global styles + index.html

**Files:**
- Modify: `frontend/src/style.css`
- Modify: `frontend/index.html`

- [ ] **Step 1: Write new global style.css with glassmorphism theme**

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, #e8f0fe 0%, #f0e8ff 50%, #fffbf5 100%);
  min-height: 100vh;
  color: #1e293b;
}

#app {
  min-height: 100vh;
}

button {
  cursor: pointer;
  border: none;
  font-family: inherit;
  font-size: 14px;
  transition: all 0.2s ease;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

input {
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s ease;
}

input:focus {
  border-color: #4a6cf7 !important;
}

/* Glass card base */
.glass-card {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.3);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.5);
}
```

- [ ] **Step 2: Update index.html title**

```html
<title>Coding Coach - 在线编码考核</title>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/style.css frontend/index.html
git commit -m "feat: add glassmorphism global styles and update site title"
```

---

### Task 3: Create NavBar.vue

**Files:**
- Create: `frontend/src/NavBar.vue`

- [ ] **Step 1: Write NavBar.vue**

```vue
<template>
  <nav class="navbar">
    <div class="navbar-brand" @click="$emit('home')">
      <span class="navbar-logo">C</span>
      <span class="navbar-title">Coding Coach</span>
    </div>
    <div class="navbar-actions">
      <template v-if="loggedIn">
        <span class="navbar-user">{{ username }}</span>
        <button class="btn-logout" @click="$emit('logout')">退出</button>
      </template>
      <template v-else>
        <button class="btn-outline" @click="$emit('login-click')">登录</button>
        <button class="btn-primary" @click="$emit('register-click')">注册</button>
      </template>
    </div>
  </nav>
</template>

<script setup>
defineProps({
  loggedIn: Boolean,
  username: { type: String, default: '' }
})
defineEmits(['login-click', 'register-click', 'logout', 'home'])
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  padding: 0 32px;
  height: 64px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.navbar-logo {
  width: 34px;
  height: 34px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 16px;
}

.navbar-title {
  font-weight: 700;
  font-size: 18px;
  color: #1e293b;
}

.navbar-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

.navbar-user {
  color: #475569;
  font-size: 14px;
  font-weight: 500;
  margin-right: 4px;
}

.btn-outline {
  padding: 8px 22px;
  background: transparent;
  border: 1px solid #4a6cf7;
  color: #4a6cf7;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
}
.btn-outline:hover {
  background: rgba(74, 108, 247, 0.06);
}

.btn-primary {
  padding: 8px 22px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
}
.btn-primary:hover {
  opacity: 0.9;
}

.btn-logout {
  padding: 8px 18px;
  background: #f1f5f9;
  color: #64748b;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
}
.btn-logout:hover {
  background: #e2e8f0;
  color: #475569;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/NavBar.vue
git commit -m "feat: add NavBar component with glassmorphism style"
```

---

### Task 4: Create ArticleCard.vue

**Files:**
- Create: `frontend/src/ArticleCard.vue`

- [ ] **Step 1: Write ArticleCard.vue**

```vue
<template>
  <div class="article-card" @click="$emit('select', article)">
    <div class="article-icon">{{ icon }}</div>
    <div class="article-title">{{ article.title }}</div>
    <div class="article-filename">{{ article.filename }}</div>
    <span v-if="tag" class="article-tag">{{ tag }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  article: { type: Object, required: true }
})
defineEmits(['select'])

const ICON_MAP = {
  'deep-face-search.md': '🔍',
  'advanced-short-url.md': '🔗'
}

const TAG_MAP = {
  'deep-face-search.md': 'AI · 算法',
  'advanced-short-url.md': '后端 · 系统设计'
}

const icon = computed(() => ICON_MAP[props.article.filename] || '📄')
const tag = computed(() => TAG_MAP[props.article.filename] || '')
</script>

<style scoped>
.article-card {
  flex: 0 0 260px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  padding: 28px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.article-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(74, 108, 247, 0.1);
  border-color: rgba(74, 108, 247, 0.2);
}

.article-icon {
  font-size: 40px;
  margin-bottom: 4px;
}

.article-title {
  font-weight: 600;
  font-size: 15px;
  color: #1e293b;
  line-height: 1.4;
}

.article-filename {
  font-size: 11px;
  color: #94a3b8;
  font-family: monospace;
}

.article-tag {
  display: inline-block;
  padding: 3px 10px;
  background: rgba(74, 108, 247, 0.08);
  color: #4a6cf7;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  margin-top: 4px;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/ArticleCard.vue
git commit -m "feat: add ArticleCard component with glass card style"
```

---

### Task 5: Create ArticleSidebar.vue

**Files:**
- Create: `frontend/src/ArticleSidebar.vue`

- [ ] **Step 1: Write ArticleSidebar.vue**

```vue
<template>
  <div class="sidebar-overlay" @click.self="$emit('close')">
    <div class="sidebar-panel">
      <!-- Header -->
      <div class="sidebar-header">
        <div class="sidebar-title-row">
          <span class="sidebar-icon">{{ icon }}</span>
          <div>
            <div class="sidebar-title">{{ article.title }}</div>
            <span v-if="tag" class="article-tag">{{ tag }}</span>
          </div>
        </div>
        <button class="sidebar-close" @click="$emit('close')">✕</button>
      </div>

      <!-- Content -->
      <div class="sidebar-body">
        <div class="sidebar-section">
          <div class="section-label">题目简介</div>
          <p class="section-text">{{ article.description }}</p>
        </div>
      </div>

      <!-- Footer -->
      <div class="sidebar-footer">
        <button class="btn-enter" @click="$emit('enter-exam', article)">
          进入考试
        </button>
        <p class="footer-hint">进入考试将启动在线编码环境</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  article: { type: Object, required: true }
})
defineEmits(['close', 'enter-exam'])

const ICON_MAP = {
  'deep-face-search.md': '🔍',
  'advanced-short-url.md': '🔗'
}

const TAG_MAP = {
  'deep-face-search.md': 'AI · 算法',
  'advanced-short-url.md': '后端 · 系统设计'
}

const icon = computed(() => ICON_MAP[props.article.filename] || '📄')
const tag = computed(() => TAG_MAP[props.article.filename] || '')
</script>

<style scoped>
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.2);
  z-index: 200;
  display: flex;
  justify-content: flex-end;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.sidebar-panel {
  width: 400px;
  height: 100%;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-left: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: -8px 0 40px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  animation: slideIn 0.25s ease;
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 28px 28px 20px;
  border-bottom: 1px solid #f1f5f9;
}

.sidebar-title-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.sidebar-icon {
  font-size: 32px;
  line-height: 1;
}

.sidebar-title {
  font-weight: 700;
  font-size: 18px;
  color: #1e293b;
  margin-bottom: 6px;
}

.article-tag {
  display: inline-block;
  padding: 2px 10px;
  background: rgba(74, 108, 247, 0.08);
  color: #4a6cf7;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
}

.sidebar-close {
  width: 32px;
  height: 32px;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}
.sidebar-close:hover {
  background: #e2e8f0;
  color: #64748b;
}

.sidebar-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px 28px;
}

.sidebar-section {
  margin-bottom: 24px;
}

.section-label {
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.section-text {
  font-size: 14px;
  color: #334155;
  line-height: 1.8;
  margin: 0;
}

.sidebar-footer {
  padding: 20px 28px;
  border-top: 1px solid #f1f5f9;
}

.btn-enter {
  width: 100%;
  padding: 13px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}
.btn-enter:hover {
  opacity: 0.9;
}

.footer-hint {
  text-align: center;
  font-size: 11px;
  color: #94a3b8;
  margin: 10px 0 0;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/ArticleSidebar.vue
git commit -m "feat: add ArticleSidebar panel for article description preview"
```

---

### Task 6: Create AuthModal.vue

**Files:**
- Create: `frontend/src/AuthModal.vue`
- Delete: `frontend/src/Login.vue`

- [ ] **Step 1: Write AuthModal.vue (replaces Login.vue)**

```vue
<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-panel">
      <!-- Header -->
      <div class="modal-header">
        <h3 class="modal-title">{{ isRegister ? '注册' : '登录' }}</h3>
        <button class="modal-close" @click="$emit('close')">✕</button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="modal-form">
        <div v-if="isRegister" class="form-group">
          <label class="form-label">姓名</label>
          <input
            v-model="form.name"
            type="text"
            class="form-input"
            placeholder="请输入姓名"
            required
          />
        </div>
        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input
            v-model="form.email"
            type="email"
            class="form-input"
            placeholder="请输入邮箱"
            required
          />
        </div>
        <div class="form-group">
          <label class="form-label">密码</label>
          <input
            v-model="form.password"
            type="password"
            class="form-input"
            placeholder="请输入密码"
            required
          />
        </div>

        <div v-if="error" class="form-error">{{ error }}</div>

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? '处理中...' : (isRegister ? '注册' : '登录') }}
        </button>
      </form>

      <!-- Toggle -->
      <div class="modal-toggle">
        <span v-if="isRegister">已有账号？</span>
        <span v-else>还没有账号？</span>
        <a @click="toggleMode">{{ isRegister ? '去登录' : '去注册' }}</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['login', 'close'])
const API_BASE = 'http://localhost:8000'

const isRegister = ref(false)
const loading = ref(false)
const error = ref('')
const form = ref({ name: '', email: '', password: '' })

const toggleMode = () => {
  isRegister.value = !isRegister.value
  error.value = ''
  form.value = { name: '', email: '', password: '' }
}

const handleSubmit = async () => {
  error.value = ''
  loading.value = true
  try {
    const endpoint = isRegister.value ? '/auth/register' : '/auth/login'
    const body = isRegister.value
      ? { name: form.value.name, email: form.value.email, password: form.value.password }
      : { email: form.value.email, password: form.value.password }

    const res = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || '请求失败')

    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify(data.user))
    emit('login', data.user)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 300;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-panel {
  width: 400px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.6);
  animation: scaleIn 0.2s ease;
}

@keyframes scaleIn {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.modal-title {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.modal-close {
  width: 32px;
  height: 32px;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
.modal-close:hover {
  background: #e2e8f0;
  color: #64748b;
}

.form-group {
  margin-bottom: 18px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  color: #1e293b;
  box-sizing: border-box;
}

.form-input::placeholder {
  color: #94a3b8;
}

.form-error {
  color: #ef4444;
  font-size: 13px;
  text-align: center;
  margin-bottom: 16px;
}

.btn-submit {
  width: 100%;
  padding: 13px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}
.btn-submit:hover:not(:disabled) {
  opacity: 0.9;
}
.btn-submit:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.modal-toggle {
  margin-top: 20px;
  text-align: center;
  font-size: 13px;
  color: #64748b;
}

.modal-toggle a {
  color: #4a6cf7;
  cursor: pointer;
  font-weight: 500;
  margin-left: 4px;
}
.modal-toggle a:hover {
  text-decoration: underline;
}
</style>
```

- [ ] **Step 2: Delete Login.vue**

```bash
rm frontend/src/Login.vue
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/AuthModal.vue frontend/src/Login.vue
git commit -m "feat: add AuthModal component replacing Login.vue"
```

---

### Task 7: Restructure App.vue

**Files:**
- Modify: `frontend/src/App.vue`

This is the central restructuring — the new App.vue manages: NavBar, article grid, sidebar, auth modal, auth guard, and exam view.

- [ ] **Step 1: Rewrite App.vue**

```vue
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
const token = ref('')

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
  token.value = ''
}

const goHome = () => {
  currentExam.value = null
  selectedArticle.value = null
}

const getHeaders = () => {
  const t = localStorage.getItem('token')
  return t ? { 'Authorization': `Bearer ${t}` } : {}
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
    token.value = savedToken
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
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/App.vue
git commit -m "feat: restructure App.vue with new layout, sidebar, and auth flow"
```

---

### Task 8: Update Exam.vue styles

**Files:**
- Modify: `frontend/src/Exam.vue`

Adapt the dark theme to match the new glassmorphism light theme. Keep all logic identical.

- [ ] **Step 1: Update Exam.vue styles**

Change the `id="exam"` container:
```css
#exam {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}
```

Change `#exam-topbar`:
```css
#exam-topbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0 28px;
  height: 60px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}
```

Change `.exam-title`:
```css
.exam-title {
  color: #1e293b;
  font-weight: 600;
  font-size: 15px;
  margin-right: auto;
}
```

Change `.back-btn`:
```css
.back-btn {
  padding: 6px 16px;
  background: #f1f5f9;
  color: #64748b;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
}
.back-btn:hover {
  background: #e2e8f0;
  color: #475569;
}
```

Change `.exam-timer` text color to `#4a6cf7` instead of `#4ecca3`.

Change `.finish-btn`:
```css
.finish-btn {
  padding: 8px 22px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.finish-btn:hover {
  opacity: 0.9;
}
```

Update loading spinner colors to match the new theme:
```css
#exam-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: #f8fafc;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #4a6cf7;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.loading-text {
  color: #64748b;
  margin-top: 16px;
  font-size: 14px;
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/Exam.vue
git commit -m "style: adapt Exam.vue to light glassmorphism theme"
```

---

### Task 9: Verify all changes work together

- [ ] **Step 1: Start backend and frontend, verify the full flow**

```bash
# Terminal 1: backend
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2: frontend
cd frontend && npm run dev
```

- [ ] **Step 2: Verify test scenarios**
  1. Page loads → shows article grid (no auth required)
  2. NavBar shows Login/Register buttons (not logged in)
  3. Click article → sidebar slides in with description
  4. Click "进入考试" while not logged in → auth guard modal
  5. Click "去登录" → auth modal opens
  6. Register → modal closes, NavBar shows username
  7. Click article → click "进入考试" → Exam page loads
  8. Click "退出" → returns to main page, NavBar shows Login/Register

- [ ] **Step 3: Final commit for any fixes**

```bash
git add -A && git commit -m "fix: resolve issues found during integration testing"
```
