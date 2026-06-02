<template>
  <div class="stat-card" :style="{ borderLeftColor: color }">
    <div class="stat-label">{{ label }}</div>
    <div class="stat-value">{{ value }}</div>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  color: { type: String, default: '#4a6cf7' }
})
</script>

<style scoped>
.stat-card {
  background: #fff; border-radius: 8px; padding: 20px;
  border-left: 4px solid #4a6cf7;
}
.stat-label {
  font-size: 12px; color: #94a3b8;
  text-transform: uppercase; letter-spacing: 1px;
}
.stat-value {
  font-size: 32px; font-weight: 800; color: #0f172a; margin-top: 4px;
}
</style>
