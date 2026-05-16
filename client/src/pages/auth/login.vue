<template>
  <view class="login-page">
    <!-- 背景装饰 -->
    <view class="bg-decoration-1"></view>
    <view class="bg-decoration-2"></view>

    <view class="content-wrapper">
      <!-- Logo 区域 -->
      <view class="logo-section">
        <view class="logo-icon">
          <text class="logo-emoji">📚</text>
        </view>
        <text class="app-title">作业伙伴</text>
        <text class="app-subtitle">欢迎回来！今天准备学点什么？</text>
      </view>

      <!-- 表单卡片 -->
      <view class="form-card">
        <!-- 角色选择器（仅注册模式显示） -->
        <view v-if="isRegisterMode" class="role-tabs">
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
          <view class="form-field">
            <text class="field-label">手机号 / 用户名</text>
            <view class="input-wrapper">
              <text class="input-icon">👤</text>
              <input
                v-model="phone"
                type="number"
                placeholder="输入您的手机号"
                class="input"
                maxlength="11"
              />
            </view>
          </view>

          <view class="form-field">
            <text class="field-label">密码</text>
            <view class="input-wrapper">
              <text class="input-icon">🔒</text>
              <input
                v-model="password"
                :password="!showPassword"
                placeholder="输入您的密码"
                class="input"
              />
              <text class="toggle-password" @tap="showPassword = !showPassword">
                {{ showPassword ? '👁️' : '👁️‍🗨️' }}
              </text>
            </view>
          </view>

          <button class="btn-submit" :loading="authStore.loading" @tap="handleLogin">
            {{ isRegisterMode ? '注册' : '登录' }}
          </button>
        </view>

        <view class="mode-switch">
          <text v-if="!isRegisterMode" @tap="isRegisterMode = true">
            没有账号？<text class="link">立即注册</text>
          </text>
          <text v-else @tap="isRegisterMode = false">
            已有账号？<text class="link">返回登录</text>
          </text>
        </view>
      </view>
    </view>

    <!-- 底部协议 -->
    <view class="footer">
      <text class="footer-text">
        登录即代表您同意 <text class="link">服务协议</text> 和 <text class="link">隐私政策</text>
      </text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const phone = ref('')
const password = ref('')
const showPassword = ref(false)
const isRegisterMode = ref(false)
const selectedRole = ref<'parent' | 'student'>('student')

async function handleLogin() {
  if (!phone.value || !password.value) {
    uni.showToast({ title: '请输入手机号和密码', icon: 'none' })
    return
  }
  try {
    // 先尝试登录
    await authStore.login(phone.value, password.value)
    // 登录成功，根据用户实际角色导航
    navigateByRole()
  } catch (e: any) {
    // 登录失败，检查是否需要注册
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

.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8f9ff;
  position: relative;
  overflow: hidden;
}

// 背景装饰
.bg-decoration-1 {
  position: absolute;
  top: -10%;
  right: -10%;
  width: 256px;
  height: 256px;
  background: rgba(20, 112, 232, 0.1);
  border-radius: 50%;
  filter: blur(60px);
}

.bg-decoration-2 {
  position: absolute;
  bottom: -5%;
  left: -5%;
  width: 320px;
  height: 320px;
  background: rgba(255, 209, 103, 0.2);
  border-radius: 50%;
  filter: blur(60px);
}

.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  position: relative;
  z-index: 1;
}

// Logo 区域
.logo-section {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  background: #1470e8;
  border-radius: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  box-shadow: 0 8px 24px rgba(20, 112, 232, 0.3);
}

.logo-emoji {
  font-size: 40px;
}

.app-title {
  display: block;
  font-size: 32px;
  font-weight: 700;
  color: #111c2a;
  margin-bottom: 4px;
}

.app-subtitle {
  display: block;
  font-size: 18px;
  color: #414754;
}

// 表单卡片
.form-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 32px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 90, 194, 0.08);
  border: 1px solid #d8e3f7;
}

// 角色选择
.role-tabs {
  display: flex;
  padding: 4px;
  background: #e6eeff;
  border-radius: 16px;
  margin-bottom: 32px;
}

.role-tab {
  flex: 1;
  padding: 12px 16px;
  border-radius: 12px;
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  color: #414754;
  transition: all 0.2s;
}

.role-tab-active {
  background: #fff;
  color: #0058bd;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

// 表单
.form-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-label {
  font-size: 14px;
  font-weight: 600;
  color: #414754;
  margin-left: 4px;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: #eff4ff;
  border: 2px solid transparent;
  border-radius: 16px;
  padding: 12px 16px;
  transition: all 0.2s;
}

.input-wrapper:focus-within {
  border-color: #0058bd;
  background: #f0f7ff;
}

.input-icon {
  font-size: 20px;
  margin-right: 12px;
}

.input {
  flex: 1;
  font-size: 16px;
  color: #111c2a;
  background: transparent;
  border: none;
  padding: 0;
}

.toggle-password {
  font-size: 20px;
  padding: 4px;
}

// 提交按钮
.btn-submit {
  width: 100%;
  height: 56px;
  background: #1470e8;
  color: #fff;
  border-radius: 20px;
  font-size: 24px;
  font-weight: 600;
  border: none;
  margin-top: 20px;
  box-shadow: 0 4px 0 rgba(0, 0, 0, 0.2), 0 8px 24px rgba(20, 112, 232, 0.2);
  transition: all 0.1s;
}

.btn-submit:active {
  transform: translateY(4px);
  box-shadow: 0 0 0 rgba(0, 0, 0, 0.2), 0 4px 16px rgba(20, 112, 232, 0.2);
}

// 模式切换
.mode-switch {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #727785;
}

.mode-switch .link {
  color: #1470e8;
  font-weight: 500;
}

// 底部
.footer {
  padding: 24px;
  text-align: center;
}

.footer-text {
  font-size: 12px;
  color: #727785;
}

.link {
  text-decoration: underline;
  color: #0058bd;
}
</style>
