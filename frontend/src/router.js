import { createRouter, createWebHistory } from 'vue-router'
import Landing from './Landing.vue'
import Home from './Home.vue'
import Exam from './Exam.vue'
import Completed from './Completed.vue'

const routes = [
  // C端
  { path: '/', name: 'landing', component: Landing },
  { path: '/challenges', name: 'challenges', component: Home },
  { path: '/exam/:filename', name: 'exam', component: Exam },
  { path: '/completed/:filename', name: 'completed', component: Completed },
  { path: '/solutions', name: 'solutions', component: () => import('./Solutions.vue') },
  { path: '/contest', name: 'contest', component: () => import('./Contest.vue') },
  { path: '/leaderboard', name: 'leaderboard', component: () => import('./Leaderboard.vue') },

  // B端 (admin) - login
  { path: '/admin/login', name: 'adminLogin', component: () => import('./AdminLogin.vue') },
  // B端 (admin) - dashboard & management
  { path: '/admin/dashboard', name: 'adminDashboard', component: () => import('./AdminDashboard.vue') },
  { path: '/admin/articles', name: 'adminArticles', component: () => import('./AdminArticles.vue') },
  { path: '/admin/articles/new', name: 'adminArticleNew', component: () => import('./AdminArticleEdit.vue') },
  { path: '/admin/articles/:name/edit', name: 'adminArticleEdit', component: () => import('./AdminArticleEdit.vue') },
  { path: '/admin/exams', name: 'adminExams', component: () => import('./AdminExamSessions.vue') },
  { path: '/admin/monitor/:examId?', name: 'adminMonitor', component: () => import('./AdminMonitor.vue') },
  { path: '/admin/grading/:examId?', name: 'adminGrading', component: () => import('./AdminGrading.vue') },
  { path: '/admin/students', name: 'adminStudents', component: () => import('./AdminStudents.vue') },
  { path: '/admin/students/:id', name: 'adminStudentDetail', component: () => import('./AdminStudentDetail.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Auth guard for admin routes (except login)
router.beforeEach((to) => {
  if (to.path.startsWith('/admin') && to.name !== 'adminLogin') {
    const token = localStorage.getItem('admin_token')
    if (!token) {
      return { name: 'adminLogin' }
    }
  }
})

export default router
