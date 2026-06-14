<template>
  <view class="login-page">
    <!-- 加载中状态 -->
    <view v-if="checking" class="content-wrapper">
      <view class="logo-blob">
        <text class="logo-icon-text">📖</text>
      </view>
      <text class="app-title">作业伙伴</text>
      <text class="loading-text">正在加载...</text>
    </view>

    <!-- ========== 登录视图 ========== -->
    <view v-else-if="!isRegisterMode" class="login-view">
      <!-- 有机形状背景装饰 -->
      <view class="bg-blob bg-blob-lilac"></view>
      <view class="bg-blob bg-blob-peach"></view>

      <view class="content-wrapper">
        <!-- Logo 区域 -->
        <view class="logo-blob">
          <text class="logo-icon-text">📖</text>
        </view>
        <text class="app-title">作业伙伴</text>
        <text class="app-subtitle">欢迎回来！今天准备学点什么？</text>

        <!-- 登录卡片 -->
        <view class="form-card">
          <!-- 角色选择器 -->
          <view class="role-tabs">
            <view
              :class="['role-tab', selectedRole === 'student' ? 'role-tab-active' : '']"
              @tap="selectedRole = 'student'"
            >
              <text>我是学生</text>
            </view>
            <view
              :class="['role-tab', selectedRole === 'parent' ? 'role-tab-active' : '']"
              @tap="selectedRole = 'parent'"
            >
              <text>我是家长</text>
            </view>
          </view>

          <!-- 表单 -->
          <view class="form-section">
            <!-- 用户名 -->
            <view class="input-wrapper">
              <text class="input-icon">👤</text>
              <input
                v-model="phone"
                type="text"
                placeholder="手机号/用户名"
                class="input"
                maxlength="11"
              />
            </view>

            <!-- 密码 -->
            <view class="input-wrapper">
              <text class="input-icon">🔒</text>
              <input
                v-model="password"
                :password="!showPassword"
                placeholder="密码"
                class="input"
              />
              <text class="toggle-password" @tap="showPassword = !showPassword">
                {{ showPassword ? '👁️' : '👁️‍🗨️' }}
              </text>
            </view>
          </view>

          <!-- 登录按钮 -->
          <button class="btn-primary-pill" :loading="authStore.loading" @tap="handleLogin">
            登录
          </button>

          <!-- 底部链接 -->
          <view class="login-footer">
            <text class="footer-link-secondary">忘记密码？</text>
            <text class="footer-link-primary" @tap="isRegisterMode = true">没有账号？去注册</text>
          </view>
        </view>
      </view>
    </view>

    <!-- ========== 注册视图 ========== -->
    <view v-else class="register-view">
      <!-- 顶部渐变有机形状背景 -->
      <view class="register-header-blob"></view>

      <view class="content-wrapper register-content">
        <!-- 注册卡片 -->
        <view class="register-card">
          <!-- 图标 & 标题 -->
          <view class="register-header">
            <view class="register-icon-wrap">
              <text class="register-icon-text">🏫</text>
            </view>
            <view class="register-title-row">
              <text class="app-title">作业伙伴</text>
              <text class="bounce-emoji">😄</text>
            </view>
            <text class="register-subtitle">创建账号，开启学习之旅</text>
          </view>

          <!-- 角色选择器 -->
          <view class="role-tabs role-tabs-register">
            <view
              :class="['role-tab', selectedRole === 'student' ? 'role-tab-active' : '']"
              @tap="selectedRole = 'student'"
            >
              <text>我是学生</text>
            </view>
            <view
              :class="['role-tab', selectedRole === 'parent' ? 'role-tab-active' : '']"
              @tap="selectedRole = 'parent'"
            >
              <text>我是家长</text>
            </view>
          </view>

          <!-- 表单 -->
          <view class="form-section">
            <!-- 手机号 -->
            <view class="input-wrapper input-wrapper-register">
              <text class="input-icon">📱</text>
              <input
                v-model="phone"
                type="number"
                placeholder="请输入手机号"
                class="input"
                maxlength="11"
              />
            </view>

            <!-- 密码 -->
            <view class="input-wrapper input-wrapper-register">
              <text class="input-icon">🔒</text>
              <input
                v-model="password"
                :password="!showPassword"
                placeholder="设置密码"
                class="input"
              />
              <text class="toggle-password" @tap="showPassword = !showPassword">
                {{ showPassword ? '👁️' : '👁️‍🗨️' }}
              </text>
            </view>
          </view>

          <!-- 注册按钮 -->
          <button class="btn-register" :loading="authStore.loading" @tap="handleLogin">
            注册
          </button>

          <!-- 底部链接 -->
          <view class="register-footer">
            <text class="footer-link-secondary footer-link-underline" @tap="isRegisterMode = false">已有账号？去登录</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const phone = ref('')
const password = ref('')
const showPassword = ref(false)
const isRegisterMode = ref(false)
const selectedRole = ref<'parent' | 'student'>('student')
const checking = ref(true)

onMounted(async () => {
  await authStore.init()
  if (authStore.user) {
    navigateByRole()
  } else {
    checking.value = false
  }
})

async function handleLogin() {
  if (!phone.value || !password.value) {
    uni.showToast({ title: '请输入手机号和密码', icon: 'none' })
    return
  }
  try {
    await authStore.login(phone.value, password.value)
    navigateByRole()
  } catch (e: any) {
    if (isRegisterMode.value) {
      try {
        await authStore.register(phone.value, password.value, selectedRole.value)
        navigateByRole()
      } catch (regError: any) {
        uni.showToast({ title: regError.message, icon: 'none' })
      }
    } else {
      uni.showToast({ title: e.message, icon: 'none' })
    }
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

// ============================================
// Shared
// ============================================
.login-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  background: $color-organic-bg;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0px 24px;
  position: relative;
  z-index: 1;
  min-height: 100vh;
}

.app-title {
  display: block;
  font-size: 24px;
  font-weight: 600;
  color: $color-organic-on-surface;
  line-height: 32px;
}

.app-subtitle {
  display: block;
  font-size: 14px;
  color: $color-organic-text-secondary;
  line-height: 20px;
  margin-top: 4px;
  text-align: center;
}

.loading-text {
  display: block;
  font-size: 14px;
  color: $color-organic-text-secondary;
  margin-top: 16px;
}

// Logo - 有机形状
.logo-blob {
  width: 128px;
  height: 128px;
  background: $color-soft-lilac;
  border-radius: 41% 59% 70% 30% / 32% 40% 60% 68%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
  box-shadow: $shadow-soft;
  animation: morph 8s ease-in-out infinite alternate;
}

.logo-icon-text {
  font-size: 48px;
}

// 角色选择器
.role-tabs {
  display: flex;
  padding: 4px;
  background: $color-organic-surface-container-low;
  border-radius: 9999px;
  margin-bottom: 32px;
  width: 100%;
}

.role-tabs-register {
  border: 1px solid rgba($color-organic-outline-variant, 0.3);
  margin-bottom: 24px;
}

.role-tab {
  flex: 1;
  padding: 12px 0;
  border-radius: 9999px;
  text-align: center;
  font-size: 14px;
  font-weight: 400;
  color: $color-organic-on-surface-variant;
  transition: all 0.2s;
}

.role-tab-active {
  background: $color-mint-green;
  color: $color-organic-on-secondary-container;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

// 表单
.form-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
  width: 100%;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: $color-organic-surface-container-lowest;
  border: 1px solid $color-organic-surface-container;
  border-radius: 16px;
  padding: 14px 16px;
  transition: all 0.2s;
}

.input-wrapper-register {
  border-width: 2px;
  border-color: $color-organic-surface-container-high;
}

.input-icon {
  font-size: 20px;
  margin-right: 12px;
}

.input {
  flex: 1;
  font-size: 14px;
  color: $color-organic-on-surface;
  background: transparent;
  border: none;
  padding: 0;
}

.toggle-password {
  font-size: 20px;
  padding: 4px;
}

// 登录按钮 - 黑色胶囊
.btn-primary-pill {
  width: 100%;
  height: 56px;
  background: $color-organic-primary;
  color: $color-organic-on-primary;
  border-radius: 9999px;
  font-size: 18px;
  font-weight: 500;
  border: none;
  box-shadow: $shadow-soft;
  transition: all 0.15s;
}

.btn-primary-pill:active {
  opacity: 0.9;
  transform: scale(0.98);
}

// 底部链接
.login-footer {
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-top: 24px;
  padding: 0 8px;
}

.footer-link-secondary {
  font-size: 14px;
  color: $color-organic-text-secondary;
}

.footer-link-primary {
  font-size: 14px;
  color: $color-organic-primary;
  font-weight: 500;
}

.footer-link-underline {
  font-weight: 600;
  border-bottom: 1px solid transparent;
}

// ============================================
// 登录视图 - 有机形状背景
// ============================================
.login-view {
  min-height: 100vh;
  position: relative;
}

.bg-blob {
  position: absolute;
  z-index: 0;
  filter: blur(80px);
  animation: morph 8s ease-in-out infinite alternate;
}

.bg-blob-lilac {
  top: -10%;
  right: -10%;
  width: 500px;
  height: 500px;
  background: rgba($color-soft-lilac, 0.3);
}

.bg-blob-peach {
  bottom: -10%;
  left: -10%;
  width: 400px;
  height: 400px;
  background: rgba($color-pale-peach, 0.3);
}

// 登录卡片
.form-card {
  width: 100%;
  max-width: 400px;
  background: $color-organic-surface-container-lowest;
  border-radius: 24px;
  padding: 32px 24px;
  box-shadow: $shadow-soft;
  display: flex;
  flex-direction: column;
  align-items: center;
}

// ============================================
// 注册视图
// ============================================
.register-view {
  min-height: 100vh;
  position: relative;
  background: $color-organic-bg;
}

// 顶部渐变有机形状
.register-header-blob {
  position: absolute;
  top: -10%;
  left: -10%;
  width: 120%;
  height: 384px;
  background: linear-gradient(135deg, $color-soft-lilac, $color-mint-green-dim);
  opacity: 0.6;
  z-index: 0;
  border-radius: 43% 57% 70% 30% / 30% 30% 70% 70%;
  animation: morph 12s ease-in-out infinite alternate;
}

.register-content {
  justify-content: center;
}

.register-card {
  width: 100%;
  max-width: 400px;
  background: $color-organic-surface-container-lowest;
  border-radius: 32px;
  padding: 24px;
  box-shadow: $shadow-diffused;
  border: 1px solid rgba($color-mint-green-focus, 0.3);
  position: relative;
  z-index: 1;
}

// 注册头部
.register-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
}

.register-icon-wrap {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, $color-soft-lilac, $color-pale-peach);
  border-radius: 40%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.register-icon-text {
  font-size: 40px;
}

.register-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bounce-emoji {
  font-size: 24px;
  animation: bounce-emoji 2s ease-in-out infinite;
}

.register-subtitle {
  font-size: 14px;
  color: $color-organic-on-surface-variant;
  font-weight: 500;
  margin-top: 4px;
  text-align: center;
}

// 注册按钮 - 黑色圆角
.btn-register {
  width: 100%;
  height: 56px;
  background: $color-organic-primary;
  color: $color-organic-on-primary;
  border-radius: 16px;
  font-size: 18px;
  font-weight: 500;
  border: none;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  margin-top: 8px;
  transition: all 0.2s;
}

.btn-register:active {
  transform: scale(0.98);
}

.register-footer {
  text-align: center;
  margin-top: 24px;
}

// ============================================
// Animations
// ============================================
@keyframes morph {
  0% {
    border-radius: 41% 59% 70% 30% / 32% 40% 60% 68%;
  }
  50% {
    border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
  }
  100% {
    border-radius: 30% 70% 50% 50% / 50% 60% 40% 50%;
  }
}

@keyframes bounce-emoji {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}
</style>
