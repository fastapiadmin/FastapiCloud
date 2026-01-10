import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import Layout from '@/layout/index.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/',
    name: 'layout',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {        
        path: '/dashboard',        
        name: 'dashboard',        
        meta: { 
          icon: 'HomeFilled' 
        },        
        component: () => import('@/views/dashboard/index.vue')      
      },      
      {        
        path: '/users',        
        name: 'users',        
        meta: { 
          icon: 'User' 
        },        
        component: () => import('@/views/user/index.vue')      
      },
      {
        path: '/users/:id',
        name: 'user-detail',
        component: () => import('@/views/user/detail.vue'),
        meta: { title: '用户详情' }
      }
    ]
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/login/index.vue'),
    meta: { requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const isAuthenticated = !!localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    // 需要认证但未登录，重定向到登录页
    next({ name: 'login' })
  } else if (to.path === '/login' && isAuthenticated) {
    // 已登录但访问登录页，重定向到首页
    next({ name: 'dashboard' })
  } else {
    // 其他情况正常导航
    next()
  }
})

export default router