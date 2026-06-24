<template>
  <nav class="navbar">
    <div class="navbar-brand" @click="$emit('home')">
      <span class="navbar-logo">AI</span>
      <span class="navbar-title">AI Done</span>
    </div>
    <div class="navbar-links">
      <router-link to="/challenges" class="nav-link" active-class="nav-link--active">题库</router-link>
      <router-link to="/solutions" class="nav-link" active-class="nav-link--active">题解广场</router-link>
      <router-link to="/contest" class="nav-link" active-class="nav-link--active">竞赛</router-link>
      <router-link to="/leaderboard" class="nav-link" active-class="nav-link--active">排行榜</router-link>
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

.navbar-links {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 40px;
}

.nav-link {
  padding: 8px 16px;
  color: #64748b;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s ease;
}
.nav-link:hover {
  color: #1e293b;
  background: rgba(74, 108, 247, 0.04);
}
.nav-link--active {
  color: #4a6cf7;
  background: rgba(74, 108, 247, 0.06);
}
</style>
