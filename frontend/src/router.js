import { createRouter, createWebHistory } from 'vue-router'
import Landing from './Landing.vue'
import Home from './Home.vue'
import Exam from './Exam.vue'
import Completed from './Completed.vue'

const routes = [
  { path: '/', name: 'landing', component: Landing },
  { path: '/challenges', name: 'challenges', component: Home },
  { path: '/exam/:filename', name: 'exam', component: Exam },
  { path: '/completed/:filename', name: 'completed', component: Completed }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
