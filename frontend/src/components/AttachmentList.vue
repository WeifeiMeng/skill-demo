<template>
  <div class="att">
    <div class="att-list">
      <div v-for="f in files" :key="f" class="att-row">
        <span>{{ f }}</span>
        <button class="att-btn-del" @click="$emit('delete', f)">删除</button>
      </div>
      <div v-if="!files.length" class="att-empty">暂无附件</div>
    </div>
    <div class="att-upload">
      <input type="file" ref="fileInput" @change="handleUpload" class="att-input" />
      <button class="att-btn-upload" @click="$refs.fileInput.click()">
        {{ uploading ? '上传中...' : '选择文件上传' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({ files: { type: Array, default: () => [] }, articleName: String })
const emit = defineEmits(['uploaded', 'delete'])

const fileInput = ref(null)
const uploading = ref(false)
const API_BASE = 'http://localhost:8000'

const getHeaders = () => {
  const t = localStorage.getItem('admin_token')
  return t ? { Authorization: `Bearer ${t}` } : {}
}

const handleUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await fetch(
      `${API_BASE}/admin/articles/${props.articleName}/attachments`,
      { method: 'POST', headers: getHeaders(), body: formData }
    )
    if (res.ok) emit('uploaded', file.name)
  } catch (err) { console.error(err) }
  finally { uploading.value = false; e.target.value = '' }
}
</script>

<style scoped>
.att-list { margin-bottom: 16px; }
.att-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 12px; background: #f8fafc; border-radius: 6px;
  font-size: 13px; color: #475569; margin-bottom: 6px;
}
.att-btn-del { background: none; border: none; color: #ef4444; font-size: 12px; }
.att-empty { color: #94a3b8; font-size: 13px; padding: 12px 0; }
.att-input { display: none; }
.att-btn-upload {
  padding: 8px 16px; background: #f1f5f9; color: #475569;
  border: 1px dashed #cbd5e1; border-radius: 6px; font-size: 13px;
}
</style>
