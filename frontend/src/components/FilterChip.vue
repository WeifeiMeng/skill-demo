<template>
  <button
    class="filter-chip"
    :class="{ 'filter-chip--active': modelValue }"
    type="button"
    @click="$emit('update:modelValue', !modelValue)"
  >
    {{ label }}
  </button>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true,
  },
  modelValue: {
    type: Boolean,
    default: false,
  },
});

defineEmits(['update:modelValue']);
</script>

<style scoped>
.filter-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 400;
  line-height: 1.4;
  cursor: pointer;
  transition: all 0.15s ease;
  outline: none;
  user-select: none;
  background: #fff;
  border: 1px solid #e2e8f0;
  color: #64748b;
}

.filter-chip:hover {
  border-color: #cbd5e1;
}

.filter-chip--active {
  background: rgba(74, 108, 247, 0.08);
  border-color: #4a6cf7;
  color: #4a6cf7;
  font-weight: 500;
}
</style>
