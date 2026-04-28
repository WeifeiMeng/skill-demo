<template>
  <div id="login">
    <div class="login-box">
      <h1>{{ isRegister ? 'Register' : 'Dev Environment' }}</h1>
      <form @submit.prevent="handleSubmit">
        <div v-if="isRegister" class="form-group">
          <label for="name">Name</label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            placeholder="Enter your name"
            required
          />
        </div>
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="Enter email"
            required
          />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="Enter password"
            required
          />
        </div>
        <div v-if="error" class="error">{{ error }}</div>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Processing...' : (isRegister ? 'Register' : 'Login') }}
        </button>
      </form>
      <div class="toggle-mode">
        <a @click="toggleMode">
          {{ isRegister ? 'Already have account? Login' : 'No account? Register' }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['login'])
const API_BASE = 'http://localhost:8000'

const isRegister = ref(false)
const loading = ref(false)
const error = ref('')
const form = ref({
  name: '',
  email: '',
  password: ''
})

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

    if (!res.ok) {
      throw new Error(data.detail || 'Request failed')
    }

    // 保存 token
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
#login {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #1a1a2e;
}

.login-box {
  background: #16213e;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 400px;
}

h1 {
  color: #e94560;
  margin: 0 0 30px 0;
  text-align: center;
  font-size: 24px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  color: #a0a0a0;
  margin-bottom: 8px;
  font-size: 14px;
}

input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #0f3460;
  border-radius: 8px;
  background: #0f3460;
  color: #fff;
  font-size: 16px;
  box-sizing: border-box;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #e94560;
}

input::placeholder {
  color: #6c6c6c;
}

.error {
  color: #e94560;
  margin-bottom: 15px;
  text-align: center;
  font-size: 14px;
}

button {
  width: 100%;
  padding: 14px;
  background: #e94560;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

button:hover:not(:disabled) {
  background: #ff6b6b;
}

button:disabled {
  background: #6c6c6c;
  cursor: not-allowed;
}

.toggle-mode {
  margin-top: 20px;
  text-align: center;
}

.toggle-mode a {
  color: #4ecca3;
  cursor: pointer;
  font-size: 14px;
}

.toggle-mode a:hover {
  text-decoration: underline;
}
</style>
