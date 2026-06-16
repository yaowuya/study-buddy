import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: () => import('@/views/login/LoginView.vue'), meta: { public: true } },
    {
      path: '/',
      component: () => import('@/layouts/AdminLayout.vue'),
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', component: () => import('@/views/dashboard/DashboardView.vue') },
        { path: 'users', component: () => import('@/views/users/UserListView.vue') },
        { path: 'users/:id', component: () => import('@/views/users/UserDetailView.vue') },
        { path: 'families', component: () => import('@/views/families/FamilyListView.vue') },
        { path: 'families/:id', component: () => import('@/views/families/FamilyDetailView.vue') },
        { path: 'tasks', component: () => import('@/views/tasks/TaskListView.vue') },
        { path: 'tasks/:id', component: () => import('@/views/tasks/TaskDetailView.vue') },
        { path: 'password', component: () => import('@/views/password/PasswordView.vue') },
      ],
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isLoggedIn()) {
    next('/login')
  } else {
    next()
  }
})

export default router
