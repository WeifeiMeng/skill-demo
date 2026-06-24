<template>
  <div class="score-bar">
    <span v-if="showScore" class="score-bar__value">{{ score }}</span>
    <div class="score-bar__track">
      <div
        class="score-bar__fill"
        :style="{ width: fillPercent + '%', background: fillColor }"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  score: {
    type: Number,
    required: true,
  },
  max: {
    type: Number,
    default: 100,
  },
  showScore: {
    type: Boolean,
    default: true,
  },
});

const fillPercent = computed(() => {
  if (props.max === 0) return 0;
  return Math.min(Math.round((props.score / props.max) * 100), 100);
});

const fillColor = computed(() => {
  if (fillPercent.value >= 80) return '#22c55e';
  if (fillPercent.value >= 50) return '#f59e0b';
  return '#ef4444';
});
</script>

<style scoped>
.score-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-bar__value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  min-width: 32px;
  text-align: right;
}

.score-bar__track {
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.score-bar__fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
  min-width: 0;
}
</style>
