<template>
  <div class="circle-progress" :style="{ width: size + 'px', height: size + 'px' }">
    <svg
      :width="size"
      :height="size"
      :viewBox="'0 0 ' + size + ' ' + size"
    >
      <circle
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        :stroke="trackColor"
        :stroke-width="strokeWidth"
      />
      <circle
        :cx="center"
        :cy="center"
        :r="radius"
        fill="none"
        :stroke="progressColor"
        :stroke-width="strokeWidth"
        stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        class="circle-progress__arc"
      />
    </svg>
    <div class="circle-progress__text">
      <span class="circle-progress__value">{{ value }}</span>
      <span class="circle-progress__separator">/</span>
      <span class="circle-progress__max">{{ max }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  value: {
    type: Number,
    required: true,
  },
  max: {
    type: Number,
    default: 100,
  },
  size: {
    type: Number,
    default: 120,
  },
});

const radius = props.size * 0.42;
const strokeWidth = props.size * 0.08;
const center = props.size / 2;
const circumference = 2 * Math.PI * radius;

const percent = computed(() => {
  if (props.max === 0) return 0;
  return Math.min(props.value / props.max, 1);
});

const dashOffset = computed(() => {
  return circumference * (1 - percent.value);
});

const trackColor = '#f0f0f0';

const progressColor = computed(() => {
  const pct = percent.value * 100;
  if (pct >= 80) return '#22c55e';
  if (pct >= 50) return '#f59e0b';
  return '#ef4444';
});
</script>

<style scoped>
.circle-progress {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.circle-progress__arc {
  transform: rotate(-90deg);
  transform-origin: center center;
  transition: stroke-dashoffset 0.6s ease;
}

.circle-progress__text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #1e293b;
}

.circle-progress__value {
  font-weight: 700;
  font-size: 22px;
}

.circle-progress__separator {
  margin: 0 2px;
  color: #94a3b8;
}

.circle-progress__max {
  font-weight: 400;
  color: #94a3b8;
  font-size: 16px;
}
</style>
