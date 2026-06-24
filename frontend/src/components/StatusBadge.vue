<template>
  <span class="status-badge" :class="'status-badge--' + variant">{{ label }}</span>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  variant: {
    type: String,
    default: 'default',
  },
});
</script>

<style scoped>
.status-badge {
  display: inline-block;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  padding: 3px 12px;
  line-height: 1.5;
  white-space: nowrap;
}

/* default */
.status-badge--default {
  background: #f1f5f9;
  color: #64748b;
}

/* active */
.status-badge--active {
  background: #dcfce7;
  color: #16a34a;
}

/* upcoming */
.status-badge--upcoming {
  background: #dbeafe;
  color: #2563eb;
}

/* ended */
.status-badge--ended {
  background: #f1f5f9;
  color: #64748b;
}

/* draft */
.status-badge--draft {
  background: #fef3c7;
  color: #b45309;
}

/* pass / solved / easy */
.status-badge--pass,
.status-badge--solved,
.status-badge--easy {
  background: #dcfce7;
  color: #16a34a;
}

/* fail / unsolved / hard */
.status-badge--fail,
.status-badge--unsolved,
.status-badge--hard {
  background: #fef2f2;
  color: #dc2626;
}

/* pending / pending_review / attempted / medium */
.status-badge--pending,
.status-badge--pending_review,
.status-badge--attempted,
.status-badge--medium {
  background: #fef3c7;
  color: #b45309;
}

/* new */
.status-badge--new {
  background: #ede9fe;
  color: #7c3aed;
}
</style>
