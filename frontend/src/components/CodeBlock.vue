<template>
  <div class="code-block-wrapper">
    <div class="code-block" ref="codeBlockRef">
      <div
        v-for="(line, index) in lines"
        :key="index"
        class="code-line"
        :class="{ 'code-line--highlighted': isHighlighted(index + 1) }"
      >
        <span class="code-line__number">{{ index + 1 }}</span>
        <span class="code-line__text">{{ line }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  code: {
    type: String,
    required: true,
  },
  highlights: {
    type: Array,
    default: () => [],
  },
})

const lines = computed(() => {
  if (!props.code) return []
  return props.code.split('\n')
})

const highlightSet = computed(() => {
  if (!props.highlights || props.highlights.length === 0) return new Set()
  return new Set(props.highlights.filter((n) => Number.isInteger(n) && n > 0))
})

function isHighlighted(lineNumber) {
  return highlightSet.value.has(lineNumber)
}
</script>

<style scoped>
.code-block-wrapper {
  width: 100%;
}

.code-block {
  background-color: #0f172a;
  border-radius: 10px;
  padding: 12px 16px;
  max-height: 300px;
  overflow: auto;
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.65;
}

.code-block::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.code-block::-webkit-scrollbar-track {
  background: transparent;
}

.code-block::-webkit-scrollbar-thumb {
  background-color: #334155;
  border-radius: 3px;
}

.code-block::-webkit-scrollbar-thumb:hover {
  background-color: #475569;
}

.code-line {
  display: flex;
  align-items: flex-start;
  min-height: 1.65em;
}

.code-line--highlighted {
  background-color: rgba(74, 108, 247, 0.12);
  margin-left: -16px;
  margin-right: -16px;
  padding-left: 16px;
  padding-right: 16px;
}

.code-line__number {
  flex-shrink: 0;
  min-width: 32px;
  text-align: right;
  padding-right: 16px;
  color: #475569;
  user-select: none;
  -webkit-user-select: none;
}

.code-line__text {
  color: #e2e8f0;
  white-space: pre;
  word-break: normal;
  overflow-wrap: normal;
}
</style>
