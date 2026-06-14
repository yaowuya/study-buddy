<template>
  <view class="bottom-nav-float">
    <view
      v-for="item in navItems"
      :key="item.key"
      :class="['nav-item', active === item.key ? 'nav-item-active' : '']"
      @tap="handleTap(item)"
    >
      <view :class="['nav-icon-wrap', active === item.key ? 'nav-icon-wrap-active' : '']">
        <text
          class="material-symbols-outlined ms-nav-icon"
          :class="active === item.key ? 'ms-fill' : ''"
        >{{ item.icon }}</text>
      </view>
      <text class="nav-label">{{ item.label }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
export interface NavItem {
  key: string
  icon: string
  label: string
  url: string
}

defineProps<{
  active: string
  navItems: NavItem[]
}>()

function handleTap(item: NavItem) {
  uni.redirectTo({ url: item.url })
}
</script>

<style lang="scss" scoped>
@use '@/static/styles/variables.scss' as *;

.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-weight: normal;
  font-style: normal;
  font-size: 28px;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.ms-fill {
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.bottom-nav-float {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 8px;
  box-shadow: 0 8px 32px rgba(185, 240, 166, 0.3);
  border: 1px solid rgba($color-mint-green-bright, 0.3);
  min-width: 280px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 16px;
  border-radius: 9999px;
  transition: all 0.2s;
  &:active { transform: scale(0.95); }
}

.nav-icon-wrap {
  width: 48px; height: 48px;
  border-radius: $radius-full;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}

.nav-icon-wrap-active {
  background: $color-mint-green-bright;
  box-shadow: 0 2px 8px rgba(185, 240, 166, 0.4);
}

.ms-nav-icon {
  font-size: 28px;
  color: rgba(29, 59, 22, 0.6);
}

.nav-item-active .ms-nav-icon {
  color: $color-dark-green;
}

.nav-label {
  font-size: 12px;
  font-weight: 600;
  margin-top: 2px;
  line-height: 16px;
  color: rgba(29, 59, 22, 0.6);
}

.nav-item-active .nav-label {
  color: $color-dark-green;
  font-weight: 700;
}
</style>
