<template>
  <div class="admin-layout">
    <aside class="admin-layout__sidebar">
      <div class="admin-layout__brand">
        <span class="admin-layout__brand-name">AI Done</span>
        <span class="admin-layout__brand-badge">管理后台</span>
      </div>
      <nav class="admin-layout__nav">
        <router-link
          to="/admin/dashboard"
          class="admin-layout__nav-link"
          :class="{ 'admin-layout__nav-link--active': activeRoute === 'dashboard' }"
        >
          仪表盘
        </router-link>
        <router-link
          to="/admin/articles"
          class="admin-layout__nav-link"
          :class="{ 'admin-layout__nav-link--active': activeRoute === 'articles' }"
        >
          题目管理
        </router-link>
        <router-link
          to="/admin/exams"
          class="admin-layout__nav-link"
          :class="{ 'admin-layout__nav-link--active': activeRoute === 'exams' }"
        >
          考试场次
        </router-link>
        <router-link
          to="/admin/monitor"
          class="admin-layout__nav-link"
          :class="{ 'admin-layout__nav-link--active': activeRoute === 'monitor' }"
        >
          实时监控
        </router-link>
        <router-link
          to="/admin/grading"
          class="admin-layout__nav-link"
          :class="{ 'admin-layout__nav-link--active': activeRoute === 'grading' }"
        >
          成绩报告
        </router-link>
        <router-link
          to="/admin/students"
          class="admin-layout__nav-link"
          :class="{ 'admin-layout__nav-link--active': activeRoute === 'students' }"
        >
          考生数据
        </router-link>
      </nav>
      <div class="admin-layout__footer">
        <button class="admin-layout__logout-btn" @click="handleLogout">退出登录</button>
        <router-link to="/challenges" class="admin-layout__back-link">&larr; 返回前台</router-link>
      </div>
    </aside>
    <main class="admin-layout__content">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

defineProps({
  activeRoute: {
    type: String,
    required: true,
    validator: (value) => ['dashboard', 'articles', 'exams', 'monitor', 'grading', 'students'].includes(value),
  },
})

const router = useRouter()

const handleLogout = () => {
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_user')
  router.push({ name: 'adminLogin' })
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
}

.admin-layout__sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 220px;
  height: 100vh;
  background-color: #ffffff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  padding-top: 24px;
  overflow-y: auto;
  z-index: 100;
}

.admin-layout__brand {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 20px;
}

.admin-layout__brand-name {
  font-size: 20px;
  font-weight: 800;
  color: #1e293b;
  letter-spacing: -0.02em;
}

.admin-layout__brand-badge {
  font-size: 11px;
  font-weight: 500;
  color: #94a3b8;
  background-color: #f1f5f9;
  padding: 2px 8px;
  border-radius: 4px;
  letter-spacing: 0.05em;
}

.admin-layout__nav {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.admin-layout__nav-link {
  display: block;
  padding: 10px 20px;
  margin: 2px 12px;
  color: #64748b;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  border-radius: 6px;
  border-left: 3px solid transparent;
  transition: background-color 0.15s ease, color 0.15s ease,
    border-color 0.15s ease;
}

.admin-layout__nav-link:hover {
  background-color: #f8fafc;
}

.admin-layout__nav-link--active {
  background-color: rgba(74, 108, 247, 0.06);
  color: #4a6cf7;
  border-left-color: #4a6cf7;
}

.admin-layout__nav-link--active:hover {
  background-color: rgba(74, 108, 247, 0.1);
}

.admin-layout__footer {
  padding: 16px 12px;
  border-top: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.admin-layout__logout-btn {
  width: 100%;
  padding: 10px;
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #64748b;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
}
.admin-layout__logout-btn:hover {
  background: #f8fafc;
  color: #475569;
}

.admin-layout__back-link {
  display: block;
  text-align: center;
  font-size: 12px;
  color: #94a3b8;
  text-decoration: none;
  padding: 6px 0;
}
.admin-layout__back-link:hover {
  color: #4a6cf7;
}

.admin-layout__content {
  margin-left: 220px;
  flex: 1;
  padding: 32px;
  max-width: 1100px;
  min-height: 100vh;
  background-color: #f8fafc;
  box-sizing: border-box;
}
</style>
