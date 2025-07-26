// --- START OF FILE frontend/src/router/index.js ---

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'AppLayout',
    meta: { requiresAuth: true },
    component: () => import('../views/AppLayout.vue'),
    children: [
      { path: '', name: 'dashboard', component: () => import('../views/DashboardView.vue') },
      { path: 'consultation', name: 'consultation', component: () => import('../views/ConsultationView.vue') },
      { path: 'chat', name: 'chat', component: () => import('../views/ChatView.vue') },
      { path: 'flock', name: 'flock', component: () => import('../views/FlockView.vue') },
      { path: 'data-management', name: 'dataManagement', component: () => import('../views/DataManagementView.vue') },
      { path: 'settings', name: 'settings', component: () => import('../views/SettingsView.vue') }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    meta: { requiresGuest: true },
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 【終極修正版】全域導航守衛
// 這個守衛確保在訪問任何頁面前，都會先完成身份驗證的檢查
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 檢查 store 是否已經初始化 (即，是否已經跑過一次 verifyAuth)
  // 我們用 isLoading 狀態來判斷。如果 isLoading 是 true，代表這是第一次加載，需要驗證。
  if (authStore.isLoading) {
    // 等待初始的身份驗證完成
    await authStore.verifyAuth()
  }

  const isAuthenticated = authStore.isAuthenticated

  // 情況一：目標路由需要登入 (requiresAuth)
  if (to.meta.requiresAuth) {
    if (isAuthenticated) {
      // 如果已登入，放行
      next()
    } else {
      // 如果未登入，跳轉到登入頁
      next('/login')
    }
  } 
  // 情況二：目標路由是給訪客的 (requiresGuest)，例如登入頁
  else if (to.meta.requiresGuest) {
    if (isAuthenticated) {
      // 如果已登入，但要去登入頁，則直接跳轉到主頁
      next('/')
    } else {
      // 如果未登入，放行
      next()
    }
  } 
  // 情況三：其他所有路由 (例如 404 頁面)，直接放行
  else {
    next()
  }
})

export default router

// --- END OF FILE frontend/src/router/index.js ---