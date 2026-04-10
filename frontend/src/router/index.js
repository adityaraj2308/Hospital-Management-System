import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth.js'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: () => import('@/views/Login.vue'), meta: { public: true } },
  { path: '/register', component: () => import('@/views/Register.vue'), meta: { public: true } },
  { path: '/admin', component: () => import('@/views/AdminDashboard.vue'), meta: { role: 'admin' } },
  { path: '/doctor', component: () => import('@/views/DoctorDashboard.vue'), meta: { role: 'doctor' } },
  { path: '/patient', component: () => import('@/views/PatientDashboard.vue'), meta: { role: 'patient' } },
  { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('hms_token')
  const role = localStorage.getItem('hms_role')

  if (to.meta.public) {
    if (token && role) {
      return next(`/${role}`)
    }
    return next()
  }

  if (!token) return next('/login')

  if (to.meta.role && to.meta.role !== role) {
    return next(`/${role}`)
  }

  next()
})

export default router
