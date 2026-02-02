import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { guestOnly: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { guestOnly: true }
    },
    {
      path: '/children',
      name: 'children',
      component: () => import('../views/ChildrenView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/child/:id',
      name: 'child-detail',
      component: () => import('../views/ChildDetailView.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: 'growth',
          name: 'growth',
          component: () => import('../components/GrowthChart.vue')
        },
        {
          path: 'photos',
          name: 'photos',
          component: () => import('../components/PhotoGallery.vue')
        },
        {
          path: 'milestones',
          name: 'milestones',
          component: () => import('../components/Milestones.vue')
        }
      ]
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 初始化认证状态
  authStore.initializeAuth()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if ((to.meta.guestOnly && authStore.isAuthenticated)) {
    next('/')
  } else {
    next()
  }
})

export default router