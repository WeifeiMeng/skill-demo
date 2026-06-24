<template>
  <div class="process-bar">
    <div class="process-bar__row">
      <div class="process-bar__left">
        <span v-if="icon" class="process-bar__icon">{{ icon }}</span>
        <span class="process-bar__label">{{ label }}</span>
      </div>
      <span class="process-bar__score">{{ score }}/{{ max }}</span>
    </div>
    <div class="process-bar__track">
      <div
        class="process-bar__fill"
        :style="{ width: fillPercent + '%' }"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  icon: {
    type: String,
    default: '',
  },
  label: {
    type: String,
    required: true,
  },
  score: {
    type: Number,
    required: true,
  },
  max: {
    type: Number,
    default: 20,
  },
});

const fillPercent = computed(() => {
  if (props.max === 0) return 0;
  return Math.min(Math.round((props.score / props.max) * 100), 100);
});
</script>

<style scoped>
.process-bar {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.process-bar__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.process-bar__left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.process-bar__icon {
  font-size: 16px;
  line-height: 1;
}

.process-bar__label {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.process-bar__score {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.process-bar__track {
  width: 100%;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.process-bar__fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #4a6cf7, #6a3de8);
  transition: width 0.4s ease;
  min-width: 0;
}
</style>
