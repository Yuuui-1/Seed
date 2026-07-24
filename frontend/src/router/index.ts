import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { resolveAuthNavigation } from './guards'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
    },
    {
      path: '/assessment/:id?',
      name: 'assessment',
      component: () => import('@/views/AssessmentView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/report/:id',
      name: 'report',
      component: () => import('@/views/ReportView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/share/:token',
      name: 'sharedReport',
      component: () => import('@/views/SharedReportView.vue'),
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('@/views/HistoryView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach((to) => {
  if (!to.meta.requiresAuth) return true
  return resolveAuthNavigation(useAuthStore().isAuthenticated, to.fullPath)
})

export default router
