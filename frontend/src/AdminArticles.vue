<template>
  <AdminLayout activeRoute="articles">
    <div class="article-list">
      <div class="page-header">
        <h2 class="page-title">题目管理</h2>
        <router-link to="/admin/articles/new" class="btn-primary">+ 新建题目</router-link>
      </div>
      <div class="card">
        <table class="table" v-if="articles.length">
          <thead>
            <tr>
              <th>文件夹</th><th>标题</th><th>附件数</th><th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in articles" :key="a.filename">
              <td><code>{{ a.filename }}</code></td>
              <td>{{ a.title || a.filename }}</td>
              <td>{{ a.attachments?.length || 0 }}</td>
              <td class="actions">
                <router-link :to="`/admin/articles/${a.filename}/edit`" class="btn-edit">编辑</router-link>
                <button class="btn-del" @click="handleDelete(a.filename)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty">暂无题目</div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminLayout from './components/AdminLayout.vue'

const API_BASE = 'http://localhost:8000'
const articles = ref([])

const getHeaders = () => {
  const t = localStorage.getItem('admin_token')
  return t ? { Authorization: `Bearer ${t}` } : {}
}

const load = async () => {
  const res = await fetch(`${API_BASE}/admin/articles`, { headers: getHeaders() })
  if (res.ok) articles.value = await res.json()
}
const handleDelete = async (filename) => {
  if (!confirm(`确认删除 "${filename}"？此操作不可恢复。`)) return
  const res = await fetch(`${API_BASE}/admin/articles/${filename}`, {
    method: 'DELETE', headers: getHeaders()
  })
  if (res.ok) await load()
}
onMounted(load)
</script>

<style scoped>
.article-list { }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.page-title { font-size: 22px; font-weight: 700; color: #0f172a; }
.btn-primary {
  padding: 10px 22px; background: #4a6cf7; color: #fff;
  border: none; border-radius: 8px; font-size: 14px; font-weight: 600;
}
.btn-primary:hover { opacity: 0.9; }
.card { background: #fff; border-radius: 10px; border: 1px solid #e2e8f0; overflow: hidden; }
.table { width: 100%; border-collapse: collapse; font-size: 13px; }
.table th { text-align: left; padding: 12px 16px; background: #f8fafc; color: #64748b; font-weight: 600; font-size: 12px; text-transform: uppercase; }
.table td { padding: 12px 16px; border-top: 1px solid #f1f5f9; color: #334155; }
.table code { background: #f1f5f9; padding: 3px 8px; border-radius: 4px; font-size: 12px; }
.actions { display: flex; gap: 8px; }
.btn-edit { padding: 5px 14px; background: #eff6ff; color: #2563eb; border-radius: 6px; font-size: 12px; font-weight: 500; }
.btn-del { padding: 5px 14px; background: #fef2f2; color: #ef4444; border: none; border-radius: 6px; font-size: 12px; font-weight: 500; }
.empty { color: #94a3b8; font-size: 13px; text-align: center; padding: 32px 0; }
</style>
