<template>
  <div id="app">
    <div id="topbar">
      <button @click="createEnv" :disabled="creating">
        {{ creating ? 'Creating...' : 'Create Dev Environment' }}
      </button>
      <button @click="loadContainers">Refresh Containers</button>
      <button v-if="activePort" @click="closePanel" class="close-btn">
        Close Panel
      </button>
    </div>

    <div id="main-content" :class="{ 'with-panel': activePort }">
      <div id="sidebar">
        <h3>Containers</h3>
        <div v-if="loading" class="loading">Loading...</div>
        <div v-else-if="containers.length === 0" class="no-containers">
          No containers yet
        </div>
        <div v-else id="container-list">
          <div
            v-for="c in containers"
            :key="c.container_id"
            class="container-item"
            :class="[c.status, { active: activePort === c.port }]"
          >
            <div class="container-info" @click="openContainer(c)">
              <div class="container-name">{{ c.name }}</div>
              <div class="container-port">Port: {{ c.port || 'N/A' }}</div>
              <div class="container-status" :class="c.status">{{ c.status }}</div>
              <div class="container-image">{{ c.image }}</div>
            </div>
            <div class="container-actions">
              <button class="menu-btn" @click.stop="toggleMenu(c.container_id)">
                ...
              </button>
              <div v-if="openMenuId === c.container_id" class="dropdown-menu">
                <button @click.stop="stopContainer(c.container_id)" :disabled="c.status !== 'running'">
                  Stop
                </button>
                <button @click.stop="removeContainer(c.container_id)" class="danger">
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activePort" id="iframe-panel">
        <iframe :src="`http://localhost:${activePort}/?folder=/home/coder/project`"></iframe>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const containers = ref([])
const loading = ref(false)
const creating = ref(false)
const activePort = ref(null)
const openMenuId = ref(null)

const API_BASE = 'http://localhost:8000'

const loadContainers = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/containers`)
    containers.value = await res.json()
  } catch (e) {
    console.error('Failed to load containers:', e)
  } finally {
    loading.value = false
  }
}

const createEnv = async () => {
  creating.value = true
  try {
    const res = await fetch(`${API_BASE}/create_env`, { method: 'POST' })
    const data = await res.json()
    await loadContainers()
    window.open(`http://localhost:${data.port}?folder=/home/coder/project`, '_blank')
  } catch (e) {
    console.error('Failed to create environment:', e)
  } finally {
    creating.value = false
  }
}

const openContainer = async (container) => {
  console.log('openContainer called:', container)
  if (!container.port) {
    console.log('No port available')
    return
  }

  // If container is not running, start it first
  if (container.status !== 'running') {
    console.log(`Container ${container.name} is ${container.status}, starting...`)
    try {
      const startRes = await fetch(`${API_BASE}/containers/${container.container_id}/start`, { method: 'POST' })
      console.log('Start response:', startRes)
      await loadContainers()
      // Wait a bit for container to start
      await new Promise(resolve => setTimeout(resolve, 2000))
    } catch (e) {
      console.error('Failed to start container:', e)
      return
    }
  }

  console.log('Setting activePort to:', container.port)
  activePort.value = container.port
}

const closePanel = () => {
  activePort.value = null
}

const toggleMenu = (containerId) => {
  openMenuId.value = openMenuId.value === containerId ? null : containerId
}

const stopContainer = async (containerId) => {
  openMenuId.value = null
  try {
    await fetch(`${API_BASE}/containers/${containerId}/stop`, { method: 'POST' })
    await loadContainers()
  } catch (e) {
    console.error('Failed to stop container:', e)
  }
}

const removeContainer = async (containerId) => {
  openMenuId.value = null
  try {
    await fetch(`${API_BASE}/containers/${containerId}/remove`, { method: 'POST' })
    if (activePort.value) {
      const container = containers.value.find(c => c.container_id === containerId)
      if (container && container.port === activePort.value) {
        activePort.value = null
      }
    }
    await loadContainers()
  } catch (e) {
    console.error('Failed to remove container:', e)
  }
}

const closeMenuOnClickOutside = (e) => {
  if (openMenuId.value && !e.target.closest('.container-actions')) {
    openMenuId.value = null
  }
}

onMounted(() => {
  loadContainers()
  document.addEventListener('click', closeMenuOnClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', closeMenuOnClickOutside)
})
</script>

<style scoped>
</style>
