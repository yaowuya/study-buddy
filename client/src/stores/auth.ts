import { defineStore } from 'pinia'
import { ref } from 'vue'
import { setToken, removeToken, getToken } from '@/utils/storage'
import * as authApi from '@/api/auth'
import type { UserOut } from '@/api/auth'
import { useHomeworkPlansStore } from '@/stores/homework-plans'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserOut | null>(null)
  const loading = ref(false)

  async function register(phone: string, password: string, role: 'parent' | 'student') {
    loading.value = true
    try {
      const res = await authApi.register({ phone, password, role })
      setToken(res.access_token)
      await fetchMe()
    } finally {
      loading.value = false
    }
  }

  async function login(phone: string, password: string) {
    loading.value = true
    try {
      const res = await authApi.login({ phone, password })
      setToken(res.access_token)
      await fetchMe()
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    try {
      user.value = await authApi.getMe()
    } catch {
      user.value = null
      removeToken()
    }
  }

  async function bind(code: string) {
    if (!user.value) return
    const fn = user.value.role === 'parent' ? authApi.bindFamily : authApi.studentBindFamily
    await fn(code)
    await fetchMe()
  }

  function logout() {
    useHomeworkPlansStore().reset()
    user.value = null
    removeToken()
    uni.reLaunch({ url: '/pages/auth/login' })
  }

  async function init() {
    if (getToken()) {
      await fetchMe()
    }
  }

  const isParent = () => user.value?.role === 'parent'
  const isStudent = () => user.value?.role === 'student'
  const isBound = () => !!user.value?.family_id

  return { user, loading, register, login, fetchMe, bind, logout, init, isParent, isStudent, isBound }
})
