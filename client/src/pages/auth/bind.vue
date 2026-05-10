<template>
  <view class="bind-page">
    <text class="title">输入家庭连接码</text>
    <text class="subtitle">请向家长获取6位连接码</text>
    <input v-model="code" type="number" placeholder="6位连接码" class="input" maxlength="6" />
    <button class="btn-primary" @tap="handleBind">绑定</button>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const code = ref('')

async function handleBind() {
  if (code.value.length !== 6) {
    uni.showToast({ title: '请输入6位连接码', icon: 'none' })
    return
  }
  try {
    await authStore.bind(code.value)
    if (authStore.isParent()) {
      uni.redirectTo({ url: '/pages/parent/dashboard' })
    } else {
      uni.redirectTo({ url: '/pages/student/home' })
    }
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}
</script>

<style lang="scss" scoped>
@import '@/static/styles/variables.scss';

.bind-page {
  padding: $spacing-xl $spacing-md;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
}

.title { font-size: $font-card-title; font-weight: 600; }
.subtitle { font-size: $font-body-md; color: $color-on-surface-variant; }

.input {
  width: 200px;
  height: $touch-min;
  text-align: center;
  font-size: 24px;
  letter-spacing: 12px;
  border: 2px solid $color-primary;
  border-radius: $radius-md;
  background: #fff;
}

.btn-primary {
  width: 200px;
  height: $touch-min;
  background: $color-primary;
  color: #fff;
  border-radius: $radius-md;
  font-size: $font-body-md;
  font-weight: 600;
  border: none;
}
</style>
