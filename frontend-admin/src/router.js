import { createRouter, createWebHistory } from 'vue-router'
import Login from './views/Login.vue'
import Dashboard from './views/Dashboard.vue'
import ArticleList from './views/ArticleList.vue'
import ArticleEdit from './views/ArticleEdit.vue'
import StudentList from './views/StudentList.vue'
import StudentDetail from './views/StudentDetail.vue'

const routes = [
  { path: '/login', name: 'login', component: Login },
  { path: '/dashboard', name: 'dashboard', component: Dashboard },
  { path: '/articles', name: 'articles', component: ArticleList },
  { path: '/articles/new', name: 'article-new', component: ArticleEdit },
  { path: '/articles/:name/edit', name: 'article-edit', component: ArticleEdit },
  { path: '/students', name: 'students', component: StudentList },
  { path: '/students/:id', name: 'student-detail', component: StudentDetail },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Auth guard: all routes except /login require token
router.beforeEach((to) => {
  const token = localStorage.getItem('admin_token')
  if (to.name !== 'login' && !token) {
    return { name: 'login' }
  }
})

export default router
