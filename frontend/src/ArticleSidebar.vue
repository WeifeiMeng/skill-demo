<template>
  <div class="sidebar-overlay" @click.self="$emit('close')">
    <div class="sidebar-panel">
      <!-- Header -->
      <div class="sidebar-header">
        <div class="sidebar-title-row">
          <span class="sidebar-icon">{{ icon }}</span>
          <div>
            <div class="sidebar-title">{{ article.title }}</div>
            <span v-if="tag" class="article-tag">{{ tag }}</span>
          </div>
        </div>
        <button class="sidebar-close" @click="$emit('close')">✕</button>
      </div>

      <!-- Content -->
      <div class="sidebar-body">
        <div class="sidebar-section">
          <div class="section-label">题目简介</div>
          <div class="section-text markdown-body" v-html="renderedDescription"></div>
        </div>
      </div>

      <!-- Footer -->
      <div class="sidebar-footer">
        <button class="btn-enter" @click="$emit('enter-exam', article)">
          进入考试
        </button>
        <p class="footer-hint">进入考试将启动在线编码环境</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  article: { type: Object, required: true }
})
defineEmits(['close', 'enter-exam'])

const ICON_MAP = {
  'deep-face-search': '🔍',
  'advanced-short-url': '🔗',
  'vibe-coding-challenge': '⚙️'
}

const TAG_MAP = {
  'deep-face-search': 'AI · 算法',
  'advanced-short-url': '后端 · 系统设计',
  'vibe-coding-challenge': '数据 · 运筹优化'
}

const icon = computed(() => ICON_MAP[props.article.filename] || '📄')
const tag = computed(() => TAG_MAP[props.article.filename] || '')
const renderedDescription = computed(() => marked(props.article.description || ''))
</script>

<style scoped>
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.2);
  z-index: 200;
  display: flex;
  justify-content: flex-end;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.sidebar-panel {
  width: 400px;
  height: 100%;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-left: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: -8px 0 40px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  animation: slideIn 0.25s ease;
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 28px 28px 20px;
  border-bottom: 1px solid #f1f5f9;
}

.sidebar-title-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.sidebar-icon {
  font-size: 32px;
  line-height: 1;
}

.sidebar-title {
  font-weight: 700;
  font-size: 18px;
  color: #1e293b;
  margin-bottom: 6px;
}

.article-tag {
  display: inline-block;
  padding: 2px 10px;
  background: rgba(74, 108, 247, 0.08);
  color: #4a6cf7;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
}

.sidebar-close {
  width: 32px;
  height: 32px;
  background: #f1f5f9;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}
.sidebar-close:hover {
  background: #e2e8f0;
  color: #64748b;
}

.sidebar-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px 28px;
}

.sidebar-section {
  margin-bottom: 24px;
}

.section-label {
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.section-text {
  font-size: 13px;
  color: #334155;
  line-height: 1.8;
}

/* Markdown rendered styles */
.markdown-body :deep(h1) { font-size: 18px; font-weight: 700; color: #1e293b; margin: 0 0 12px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; }
.markdown-body :deep(h2) { font-size: 15px; font-weight: 700; color: #1e293b; margin: 20px 0 8px; }
.markdown-body :deep(h3) { font-size: 14px; font-weight: 600; color: #334155; margin: 14px 0 6px; }
.markdown-body :deep(h4) { font-size: 13px; font-weight: 600; color: #475569; margin: 10px 0 4px; }
.markdown-body :deep(p) { margin: 0 0 8px; }
.markdown-body :deep(ul), .markdown-body :deep(ol) { margin: 4px 0 8px; padding-left: 20px; }
.markdown-body :deep(li) { margin-bottom: 2px; }
.markdown-body :deep(code) { background: #f1f5f9; padding: 1px 5px; border-radius: 4px; font-size: 12px; color: #e11d48; }
.markdown-body :deep(pre) { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; overflow-x: auto; font-size: 12px; line-height: 1.5; margin: 8px 0; }
.markdown-body :deep(pre code) { background: none; padding: 0; color: #334155; }
.markdown-body :deep(table) { width: 100%; border-collapse: collapse; font-size: 12px; margin: 8px 0; }
.markdown-body :deep(th), .markdown-body :deep(td) { border: 1px solid #e2e8f0; padding: 6px 10px; text-align: left; }
.markdown-body :deep(th) { background: #f8fafc; font-weight: 600; color: #475569; }
.markdown-body :deep(blockquote) { border-left: 3px solid #4a6cf7; padding: 4px 12px; margin: 8px 0; color: #64748b; background: #f8fafc; border-radius: 0 6px 6px 0; }
.markdown-body :deep(hr) { border: none; border-top: 1px solid #e2e8f0; margin: 12px 0; }
.markdown-body :deep(a) { color: #4a6cf7; }
.markdown-body :deep(strong) { font-weight: 600; color: #1e293b; }
.markdown-body :deep(img) { max-width: 100%; }

.sidebar-footer {
  padding: 20px 28px;
  border-top: 1px solid #f1f5f9;
}

.btn-enter {
  width: 100%;
  padding: 13px;
  background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}
.btn-enter:hover {
  opacity: 0.9;
}

.footer-hint {
  text-align: center;
  font-size: 11px;
  color: #94a3b8;
  margin: 10px 0 0;
}
</style>
