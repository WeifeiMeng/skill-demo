import { createRouter, createWebHistory } from 'vue-router'
import Home from './Home.vue'
import Exam from './Exam.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/exam/:filename', name: 'exam', component: Exam }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
