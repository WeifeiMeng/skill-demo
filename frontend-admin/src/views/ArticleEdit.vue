<template>
  <div class="article-edit">
    <div class="page-header">
      <h2 class="page-title">{{ isNew ? '新建题目' : '编辑题目：' + articleName }}</h2>
      <button class="btn-save" @click="save">保存</button>
    </div>

    <div class="field" v-if="isNew">
      <label class="field-label">文件夹名（英文标识）</label>
      <input v-model="filename" class="field-input" placeholder="my-new-article" />
    </div>

    <div class="card">
      <div class="tabs">
        <button class="tab" :class="{ active: tab === 'md' }" @click="tab = 'md'">📄 Markdown</button>
        <button class="tab" :class="{ active: tab === 'test' }" @click="tab = 'test'">🧪 测试用例</button>
        <button class="tab" :class="{ active: tab === 'att' }" @click="tab = 'att'">📎 附件</button>
      </div>

      <div v-show="tab === 'md'" class="tab-content">
        <textarea v-model="content" class="md-editor" rows="20" placeholder="# 题目名称&#10;&#10;## 题目描述&#10;..."></textarea>
      </div>

      <div v-show="tab === 'test'" class="tab-content">
        <div class="field">
          <label class="field-label">测试命令</label>
          <input v-model="testConfig.test_command" class="field-input" placeholder="python test.py" />
        </div>
        <TestCaseEditor v-model="testConfig.cases" />
      </div>

      <div v-show="tab === 'att'" class="tab-content">
        <AttachmentList
          :files="attachments"
          :articleName="articleName"
          @uploaded="attachments.push($event)"
          @delete="handleDeleteAttachment"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TestCaseEditor from '../components/TestCaseEditor.vue'
import AttachmentList from '../components/AttachmentList.vue'

const route = useRoute()
const router = useRouter()
const API_BASE = 'http://localhost:8000'

const articleName = computed(() => route.params.name || '')
const isNew = computed(() => !route.params.name)

const tab = ref('md')
const filename = ref('')
const content = ref('')
const testConfig = ref({ test_command: 'python test.py', max_score: 100, cases: [] })
const attachments = ref([])

const getHeaders = () => {
  const t = localStorage.getItem('admin_token')
  return t ? { Authorization: `Bearer ${t}` } : {}
}

onMounted(async () => {
  if (!isNew.value) {
    const res = await fetch(`${API_BASE}/admin/articles`, { headers: getHeaders() })
    if (res.ok) {
      const articles = await res.json()
      const article = articles.find(a => a.filename === articleName.value)
      if (article) {
        filename.value = article.filename
        content.value = article.content
        testConfig.value = article.test_config || { test_command: 'python test.py', max_score: 100, cases: [] }
        attachments.value = article.attachments || []
      }
    }
  }
})

const save = async () => {
  if (isNew.value) {
    if (!filename.value) { alert('请输入文件夹名'); return }
    const res = await fetch(`${API_BASE}/admin/articles`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getHeaders() },
      body: JSON.stringify({ filename: filename.value, title: filename.value, content: content.value, test_config: testConfig.value })
    })
    if (res.ok) {
      router.push({ name: 'article-edit', params: { name: filename.value } })
    } else {
      const err = await res.json()
      alert(err.detail || '创建失败')
    }
  } else {
    await fetch(`${API_BASE}/admin/articles/${articleName.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ...getHeaders() },
      body: JSON.stringify({ title: articleName.value, content: content.value, test_config: testConfig.value })
    })
    alert('保存成功')
  }
}

const handleDeleteAttachment = async (file) => {
  await fetch(`${API_BASE}/admin/articles/${articleName.value}/attachments/${file}`, {
    method: 'DELETE', headers: getHeaders()
  })
  attachments.value = attachments.value.filter(f => f !== file)
}
</script>

<style scoped>
.article-edit { max-width: 960px; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-title { font-size: 22px; font-weight: 700; color: #0f172a; }
.btn-save {
  padding: 10px 28px; background: linear-gradient(135deg, #4a6cf7, #6a3de8);
  color: #fff; border: none; border-radius: 8px; font-size: 14px; font-weight: 600;
}
.field { margin-bottom: 18px; }
.field-label { display: block; font-size: 13px; color: #475569; font-weight: 500; margin-bottom: 6px; }
.field-input {
  width: 100%; padding: 10px 14px; background: #fff; border: 1px solid #e2e8f0;
  border-radius: 8px; font-size: 14px; color: #1e293b;
}
.card { background: #fff; border-radius: 10px; border: 1px solid #e2e8f0; overflow: hidden; }
.tabs { display: flex; border-bottom: 2px solid #e2e8f0; }
.tab {
  padding: 12px 20px; background: none; border: none; border-bottom: 2px solid transparent;
  margin-bottom: -2px; color: #94a3b8; font-size: 13px; font-weight: 500;
}
.tab.active { color: #4a6cf7; border-bottom-color: #4a6cf7; font-weight: 600; }
.tab-content { padding: 24px; }
.md-editor {
  width: 100%; padding: 16px; background: #f8fafc; border: 1px solid #e2e8f0;
  border-radius: 8px; font-size: 14px; color: #1e293b; resize: vertical;
  font-family: 'SF Mono', 'Fira Code', monospace; line-height: 1.7;
}
</style>
