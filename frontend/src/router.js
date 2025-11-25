import { createRouter, createWebHistory } from 'vue-router'
import BasicGrok from './pages/BasicGrok.vue'
import PromptGrok from './pages/PromptGrok.vue'
import PromptGpt from './pages/PromptGpt.vue'
import PromptLikeGpt from './pages/PromptLikeGpt.vue'

const routes = [
  {
    path: '/',
    name: 'BasicGrok',
    component: BasicGrok
  },
  {
    path: '/about',
    name: 'PromptGrok',
    component: PromptGrok
  },
  {
    path: '/contact',
    name: 'PromptGpt',
    component: PromptGpt
  },
  {
    path: '/promptlikegpt',
    name: 'PromptLikeGpt',
    component: PromptLikeGpt
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
