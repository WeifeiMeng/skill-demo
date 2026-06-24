<template>
  <div class="rating-card">
    <div class="rating-card__main">
      <div class="rating-card__rating">{{ formattedRating }}</div>
      <div class="rating-card__tier">
        <span class="rating-card__tier-badge">{{ tierName }}</span>
      </div>
      <div class="rating-card__rank">
        全球排名 <span class="rating-card__rank-number">#{{ formattedRank }}</span> / {{ formattedTotal }}
      </div>
    </div>
    <div class="rating-card__stats">
      <slot name="stats" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  rating: {
    type: Number,
    required: true,
  },
  rank: {
    type: Number,
    required: true,
  },
  total: {
    type: Number,
    required: true,
  },
  tierName: {
    type: String,
    required: true,
  },
  tierShort: {
    type: String,
    required: true,
  },
})

const formattedRating = computed(() => {
  return Math.round(props.rating).toLocaleString()
})

const formattedRank = computed(() => {
  return props.rank.toLocaleString()
})

const formattedTotal = computed(() => {
  if (props.total >= 10000) {
    return (props.total / 10000).toFixed(0) + '万+'
  }
  return props.total.toLocaleString() + '+'
})
</script>

<style scoped>
.rating-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #0f172a, #1e293b);
  border-radius: 14px;
  padding: 24px;
  gap: 24px;
}

.rating-card__main {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

.rating-card__rating {
  font-size: 48px;
  font-weight: 800;
  color: #4a6cf7;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.rating-card__tier {
  margin-top: 6px;
}

.rating-card__tier-badge {
  display: inline-block;
  color: #38bdf8;
  background-color: rgba(56, 189, 248, 0.1);
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.rating-card__rank {
  margin-top: 8px;
  font-size: 14px;
  color: #94a3b8;
}

.rating-card__rank-number {
  color: #f1f5f9;
  font-weight: 700;
}

.rating-card__stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
  color: #94a3b8;
  font-size: 14px;
}

.rating-card__stats :deep(.stat-item) {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rating-card__stats :deep(.stat-label) {
  color: #64748b;
}

.rating-card__stats :deep(.stat-value) {
  color: #f1f5f9;
  font-weight: 600;
}

.rating-card__stats :deep(.stat-change) {
  font-weight: 600;
  font-size: 13px;
}

.rating-card__stats :deep(.stat-change--up) {
  color: #22c55e;
}

.rating-card__stats :deep(.stat-change--down) {
  color: #ef4444;
}
</style>
