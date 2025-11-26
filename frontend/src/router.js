import { createRouter, createWebHistory } from 'vue-router'
import PromptGrok from './pages/PromptGrok.vue'
import PromptGpt from './pages/PromptGpt.vue'
import PromptGemini from './pages/PromptGemini.vue'

const routes = [
  {
    path: '/',
    name: 'prompt-grok',
    component: PromptGrok
  },
  {
    path: '/prompt-gpt',
    name: 'prompt-gpt',
    component: PromptGpt
  },
  {
    path: '/prompt-gemini',
    name: 'prompt-gemini',
    component: PromptGemini
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
