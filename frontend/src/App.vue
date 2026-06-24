<template>
  <div id="app">
    <!-- NavBar: hidden on landing page and admin routes -->
    <NavBar
      v-if="!isLanding && !isAdminRoute"
      :loggedIn="loggedIn"
      :username="username"
      @login-click="showAuthModal = 'login'"
      @register-click="showAuthModal = 'register'"
      @logout="logout"
      @home="goHome"
    />

    <!-- Router View -->
    <router-view />

    <!-- Auth Modal -->
    <AuthModal
      v-if="showAuthModal"
      :initialMode="showAuthModal"
      @login="handleLogin"
      @close="showAuthModal = null"
    />
  </div>
</template>

<script setup>
import { ref, computed, provide } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import NavBar from './NavBar.vue'
import AuthModal from './AuthModal.vue'

const router = useRouter()
const route = useRoute()

// Auth state
const loggedIn = ref(false)
const username = ref('')

// Modal state
const showAuthModal = ref(null)

// Detect landing page route
const isLanding = computed(() => route.name === 'landing')

// Detect admin routes (including login)
const isAdminRoute = computed(() => route.path.startsWith('/admin'))

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
  router.push({ name: 'challenges' })
}

const goHome = () => {
  if (router.currentRoute.value.name !== 'challenges') {
    router.push({ name: 'challenges' })
  }
}

// Provide auth actions to Landing.vue (after function declarations)
provide('openAuth', (mode) => { showAuthModal.value = mode })
provide('authLoggedIn', loggedIn)
provide('authUsername', username)
provide('doLogout', logout)

// Restore session on mount
const savedToken = localStorage.getItem('token')
const savedUser = localStorage.getItem('user')
if (savedToken && savedUser) {
  try {
    const user = JSON.parse(savedUser)
    username.value = user.name
    loggedIn.value = true
  } catch (e) {
    // ignore
  }
}
</script>

<style scoped></style>
