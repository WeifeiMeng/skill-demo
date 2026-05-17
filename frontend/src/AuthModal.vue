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

const props = defineProps({
  initialMode: { type: String, default: 'login' }
})
const emit = defineEmits(['login', 'close'])
const API_BASE = 'http://localhost:8000'

const isRegister = ref(props.initialMode === 'register')
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
