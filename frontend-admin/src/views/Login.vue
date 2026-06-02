<template>
  <div class="login-page">
    <form class="login-card" @submit.prevent="handleSubmit">
      <h1 class="login-title">管理员登录</h1>
      <p class="login-subtitle">Coding Coach 管理后台</p>
      <div class="form-group">
        <label class="form-label">邮箱</label>
        <input v-model="form.email" type="email" class="form-input" placeholder="admin@example.com" required />
      </div>
      <div class="form-group">
        <label class="form-label">密码</label>
        <input v-model="form.password" type="password" class="form-input" placeholder="请输入密码" required />
      </div>
      <div v-if="error" class="form-error">{{ error }}</div>
      <button type="submit" class="btn-submit" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const API_BASE = 'http://localhost:8000'
const router = useRouter()

const form = ref({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

const handleSubmit = async () => {
  error.value = ''
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || '登录失败')
    if (data.user.role !== 'admin') throw new Error('非管理员账号，无权访问')

    localStorage.setItem('admin_token', data.token)
    localStorage.setItem('admin_user', JSON.stringify(data.user))
    router.push({ name: 'dashboard' })
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh; background: #0f172a;
}
.login-card {
  width: 400px; background: #1e293b; border-radius: 16px; padding: 40px;
  border: 1px solid #334155;
}
.login-title { font-size: 22px; font-weight: 700; color: #f1f5f9; margin-bottom: 6px; }
.login-subtitle { font-size: 14px; color: #64748b; margin-bottom: 28px; }
.form-group { margin-bottom: 18px; }
.form-label { display: block; font-size: 13px; color: #94a3b8; margin-bottom: 6px; }
.form-input {
  width: 100%; padding: 12px 14px;
  background: #0f172a; border: 1px solid #334155;
  border-radius: 10px; color: #e2e8f0; font-size: 14px; outline: none;
}
.form-input:focus { border-color: #4a6cf7; }
.form-input::placeholder { color: #475569; }
.form-error { color: #ef4444; font-size: 13px; margin-bottom: 16px; text-align: center; }
.btn-submit {
  width: 100%; padding: 13px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff; border: none; border-radius: 10px;
  font-size: 15px; font-weight: 600;
}
.btn-submit:hover:not(:disabled) { opacity: 0.9; }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
