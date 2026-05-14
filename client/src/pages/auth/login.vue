<template>
  <view class="login-page">
    <view class="logo-section">
      <text class="app-title">作业陪伴助手</text>
    </view>

    <view class="form-section">
      <input v-model="phone" type="number" placeholder="手机号" class="input" maxlength="11" />
      <input v-model="password" type="safe-password" placeholder="密码" class="input" />

      <view class="role-selector">
        <view :class="['role-btn', role === 'parent' ? 'role-active' : '']" @tap="role = 'parent'">
          <text>家长</text>
        </view>
        <view :class="['role-btn', role === 'student' ? 'role-active' : '']" @tap="role = 'student'">
          <text>学生</text>
        </view>
      </view>

      <button class="btn-primary" :loading="authStore.loading" @tap="handleLogin">登录</button>
      <button class="btn-secondary" @tap="handleRegister">注册</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const phone = ref('')
const password = ref('')
const role = ref<'parent' | 'student'>('parent')

async function handleLogin() {
  if (!phone.value || !password.value) {
    uni.showToast({ title: '请输入手机号和密码', icon: 'none' })
    return
  }
  try {
    await authStore.login(phone.value, password.value)
    navigateByRole()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

async function handleRegister() {
  if (!phone.value || !password.value) {
    uni.showToast({ title: '请输入手机号和密码', icon: 'none' })
    return
  }
  try {
    await authStore.register(phone.value, password.value, role.value)
    navigateByRole()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

function navigateByRole() {
  if (!authStore.isBound()) {
    uni.redirectTo({ url: '/pages/auth/bind' })
    return
  }
  if (authStore.isParent()) {
    uni.redirectTo({ url: '/pages/parent/dashboard' })
  } else {
    uni.redirectTo({ url: '/pages/student/home' })
  }
}
</script>

<style lang="scss" scoped>
@use '@/static/styles/variables.scss' as *;

.login-page {
  padding: $spacing-xl $spacing-md;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.logo-section { text-align: center; margin-bottom: $spacing-lg; }
.app-title { font-size: $font-hero; font-weight: 700; color: $color-primary; }

.form-section { display: flex; flex-direction: column; gap: $spacing-sm; }

.input {
  height: $touch-min;
  padding: 0 $spacing-sm;
  border: 1px solid $color-outline-variant;
  border-radius: $radius-md;
  font-size: $font-body-md;
  background: #fff;
}

.role-selector { display: flex; gap: $spacing-sm; }
.role-btn {
  flex: 1;
  height: $touch-min;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid $color-outline-variant;
  border-radius: $radius-md;
  font-size: $font-body-md;
  font-weight: 500;
}
.role-active {
  border-color: $color-primary;
  background: rgba($color-primary, 0.08);
  color: $color-primary;
}

.btn-primary {
  height: $touch-min;
  background: $color-primary;
  color: #fff;
  border-radius: $radius-md;
  font-size: $font-body-md;
  font-weight: 600;
  border: none;
}
.btn-secondary {
  height: $touch-min;
  background: transparent;
  color: $color-primary;
  border-radius: $radius-md;
  font-size: $font-body-md;
  border: 1px solid $color-primary;
}
</style>
