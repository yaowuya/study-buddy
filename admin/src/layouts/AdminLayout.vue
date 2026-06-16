<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const selectedKeys = computed(() => {
  const path = route.path
  if (path.startsWith('/users')) return ['/users']
  if (path.startsWith('/families')) return ['/families']
  if (path.startsWith('/tasks')) return ['/tasks']
  if (path === '/password') return ['/password']
  return ['/dashboard']
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

const menuItems = [
  { key: '/dashboard', label: '仪表盘', icon: '📊' },
  { key: '/users', label: '用户管理', icon: '👥' },
  { key: '/families', label: '家庭管理', icon: '🏠' },
  { key: '/tasks', label: '作业管理', icon: '📝' },
  { key: '/password', label: '修改密码', icon: '🔒' },
]
</script>

<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider theme="dark" width="200">
      <div style="height:64px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;font-weight:700;border-bottom:1px solid rgba(255,255,255,0.1)">
        📚 学伴管理台
      </div>
      <a-menu
        theme="dark"
        mode="inline"
        :selected-keys="selectedKeys"
        @click="({ key }: { key: string }) => router.push(key)"
      >
        <a-menu-item v-for="item in menuItems" :key="item.key">
          {{ item.icon }} {{ item.label }}
        </a-menu-item>
      </a-menu>
    </a-layout-sider>

    <a-layout>
      <a-layout-header style="background:#fff;padding:0 24px;display:flex;align-items:center;justify-content:space-between;box-shadow:0 1px 4px rgba(0,21,41,.08)">
        <span style="font-size:16px;font-weight:600">学伴 Admin</span>
        <a-dropdown>
          <a-button type="text">
            {{ authStore.adminInfo?.username || 'Admin' }} ▼
          </a-button>
          <template #overlay>
            <a-menu>
              <a-menu-item key="pwd" @click="router.push('/password')">修改密码</a-menu-item>
              <a-menu-divider />
              <a-menu-item key="logout" @click="handleLogout" danger>退出登录</a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </a-layout-header>
      <a-layout-content style="margin:24px;background:#f0f2f5;min-height:280px">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>
