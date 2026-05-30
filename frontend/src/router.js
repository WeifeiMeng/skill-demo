import { createRouter, createWebHistory } from 'vue-router'
import Home from './Home.vue'
import Exam from './Exam.vue'
import Completed from './Completed.vue'

const routes = [
  { path: '/', name: 'home', component: Home },
  { path: '/exam/:filename', name: 'exam', component: Exam },
  { path: '/completed/:filename', name: 'completed', component: Completed }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
