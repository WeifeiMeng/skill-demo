<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <span class="sidebar-logo">A</span>
      <span class="sidebar-title">管理后台</span>
    </div>
    <nav class="sidebar-nav">
      <router-link to="/dashboard" class="nav-item" active-class="nav-active">
        <span>📊</span> 仪表盘
      </router-link>
      <router-link to="/articles" class="nav-item" active-class="nav-active">
        <span>📝</span> 题目管理
      </router-link>
      <router-link to="/students" class="nav-item" active-class="nav-active">
        <span>👥</span> 考生数据
      </router-link>
    </nav>
    <div class="sidebar-footer">
      <button class="btn-logout" @click="logout">退出登录</button>
    </div>
  </aside>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const logout = () => {
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_user')
  router.push({ name: 'login' })
}
</script>

<style scoped>
.sidebar {
  width: 220px;
  background: #0f172a;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  padding: 24px 0;
}
.sidebar-brand {
  display: flex; align-items: center; gap: 10px;
  padding: 0 20px; margin-bottom: 32px;
}
.sidebar-logo {
  width: 34px; height: 34px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  border-radius: 8px; display: flex;
  align-items: center; justify-content: center;
  color: #fff; font-weight: 700; font-size: 16px;
}
.sidebar-title { color: #fff; font-weight: 700; font-size: 16px; }
.sidebar-nav { flex: 1; display: flex; flex-direction: column; gap: 4px; padding: 0 12px; }
.nav-item {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 12px; border-radius: 8px;
  color: #94a3b8; font-size: 14px; font-weight: 500;
  transition: all 0.15s;
}
.nav-item:hover { color: #e2e8f0; background: rgba(255,255,255,0.05); }
.nav-active { color: #818cf8; background: rgba(74,108,247,0.15); font-weight: 600; }
.sidebar-footer { padding: 0 12px; }
.btn-logout {
  width: 100%; padding: 10px;
  background: transparent; border: 1px solid #334155;
  color: #64748b; border-radius: 8px; font-size: 13px;
}
.btn-logout:hover { background: rgba(255,255,255,0.05); color: #94a3b8; }
</style>
