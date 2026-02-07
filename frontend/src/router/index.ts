import { createRouter, createWebHistory } from 'vue-router'
import UploadView from '@/views/UploadView.vue'
import DashboardView from '@/views/DashboardView.vue'
import HelpView from '@/views/HelpView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'upload',
      component: UploadView,
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
    },
    {
      path: '/help',
      name: 'help',
      component: HelpView,
    },
  ],
})

export default router
