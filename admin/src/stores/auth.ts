import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as apiLogin, getMe } from '@/api/auth'
import type { AdminOut } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('admin_token') || '')
  const adminInfo = ref<AdminOut | null>(null)

  const isLoggedIn = () => !!token.value

  async function login(username: string, password: string) {
    const res = await apiLogin(username, password)
    token.value = res.data.access_token
    localStorage.setItem('admin_token', token.value)
    await fetchMe()
  }

  async function fetchMe() {
    try {
      const res = await getMe()
      adminInfo.value = res.data
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    adminInfo.value = null
    localStorage.removeItem('admin_token')
  }

  return { token, adminInfo, isLoggedIn, login, fetchMe, logout }
})
