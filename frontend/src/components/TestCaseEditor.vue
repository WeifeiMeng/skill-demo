<template>
  <div class="tce">
    <div class="tce-list">
      <div v-for="(c, i) in modelValue" :key="i" class="tce-row">
        <input v-model="c.name" class="tce-input-name" placeholder="用例名称" />
        <input v-model.number="c.score" type="number" class="tce-input-score" placeholder="分值" />
        <button class="tce-btn-del" @click="remove(i)">✕</button>
      </div>
    </div>
    <button class="tce-btn-add" @click="add">+ 添加用例</button>
  </div>
</template>

<script setup>
const props = defineProps({ modelValue: { type: Array, default: () => [] } })
const emit = defineEmits(['update:modelValue'])

const add = () => {
  const list = [...props.modelValue, { name: '', score: 0 }]
  emit('update:modelValue', list)
}
const remove = (i) => {
  const list = props.modelValue.filter((_, idx) => idx !== i)
  emit('update:modelValue', list)
}
</script>

<style scoped>
.tce-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; }
.tce-row { display: flex; gap: 8px; align-items: center; }
.tce-input-name {
  flex: 1; padding: 8px 12px; background: #f8fafc;
  border: 1px solid #e2e8f0; border-radius: 6px; font-size: 13px;
}
.tce-input-score {
  width: 80px; padding: 8px 12px; background: #f8fafc;
  border: 1px solid #e2e8f0; border-radius: 6px; font-size: 13px;
}
.tce-btn-del {
  width: 28px; height: 28px; background: #fef2f2; color: #ef4444;
  border: none; border-radius: 6px; font-size: 14px;
}
.tce-btn-add {
  padding: 8px 16px; background: #f1f5f9; color: #475569;
  border: 1px dashed #cbd5e1; border-radius: 6px; font-size: 13px;
}
</style>
