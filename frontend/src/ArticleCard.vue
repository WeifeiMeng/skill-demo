<template>
  <div class="article-card" @click="$emit('select', article)">
    <div class="article-icon">{{ icon }}</div>
    <div class="article-title">{{ article.title }}</div>
    <div class="article-filename">{{ article.filename }}</div>
    <span v-if="tag" class="article-tag">{{ tag }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  article: { type: Object, required: true }
})
defineEmits(['select'])

const ICON_MAP = {
  'deep-face-search.md': '🔍',
  'advanced-short-url.md': '🔗'
}

const TAG_MAP = {
  'deep-face-search.md': 'AI · 算法',
  'advanced-short-url.md': '后端 · 系统设计'
}

const icon = computed(() => ICON_MAP[props.article.filename] || '📄')
const tag = computed(() => TAG_MAP[props.article.filename] || '')
</script>

<style scoped>
.article-card {
  flex: 0 0 260px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  padding: 28px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.article-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(74, 108, 247, 0.1);
  border-color: rgba(74, 108, 247, 0.2);
}

.article-icon {
  font-size: 40px;
  margin-bottom: 4px;
}

.article-title {
  font-weight: 600;
  font-size: 15px;
  color: #1e293b;
  line-height: 1.4;
}

.article-filename {
  font-size: 11px;
  color: #94a3b8;
  font-family: monospace;
}

.article-tag {
  display: inline-block;
  padding: 3px 10px;
  background: rgba(74, 108, 247, 0.08);
  color: #4a6cf7;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  margin-top: 4px;
}
</style>
