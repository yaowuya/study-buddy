<template>
  <view v-if="visible" class="modal-overlay" @tap="handleCancel">
    <view class="modal-card" @tap.stop>
      <!-- Icon -->
      <view :class="['modal-icon-wrap', `icon-${type}`]">
        <text class="material-symbols-outlined modal-icon">{{ icon }}</text>
      </view>
      <!-- Title -->
      <text class="modal-title">{{ title }}</text>
      <!-- Description -->
      <text v-if="desc" class="modal-desc">{{ desc }}</text>

      <!-- Actions: flat style (logout etc.) -->
      <view v-if="flat" class="modal-actions-flat">
        <view class="flat-cancel" @tap="handleCancel">
          <text class="flat-cancel-text">{{ cancelText }}</text>
        </view>
        <view class="flat-divider"></view>
        <view :class="['flat-confirm', `flat-confirm-${type}`]" @tap="handleConfirm">
          <text class="flat-confirm-text">{{ confirmText }}</text>
        </view>
      </view>

      <!-- Actions: rounded style (delete etc.) -->
      <view v-else class="modal-actions-rounded">
        <view class="rounded-cancel" @tap="handleCancel">
          <text class="rounded-cancel-text">{{ cancelText }}</text>
        </view>
        <view :class="['rounded-confirm', `rounded-confirm-${type}`]" @tap="handleConfirm">
          <text v-if="confirmIcon" class="material-symbols-outlined rounded-confirm-icon">{{ confirmIcon }}</text>
          <text class="rounded-confirm-text">{{ confirmText }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  visible: boolean
  /** danger = 珊瑚色删除风格, warning = 淡红退出风格, info = 浅紫信息风格 */
  type?: 'danger' | 'warning' | 'info'
  /** Material Symbol 图标名 */
  icon?: string
  title: string
  desc?: string
  confirmText?: string
  cancelText?: string
  /** 确认按钮图标（仅 rounded 模式生效） */
  confirmIcon?: string
  /** true = 扁平分割按钮(退出登录), false = 圆角胶囊按钮(删除) */
  flat?: boolean
}>(), {
  type: 'danger',
  icon: 'warning',
  desc: '',
  confirmText: '确定',
  cancelText: '取消',
  confirmIcon: '',
  flat: false,
})

const emit = defineEmits<{
  (e: 'update:visible', val: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

function handleCancel() {
  emit('update:visible', false)
  emit('cancel')
}

function handleConfirm() {
  emit('update:visible', false)
  emit('confirm')
}
</script>

<style lang="scss" scoped>
@use '@/static/styles/variables.scss' as *;

.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-weight: normal; font-style: normal; line-height: 1;
  letter-spacing: normal; text-transform: none; display: inline-block;
  white-space: nowrap; word-wrap: normal; direction: ltr;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

// ─── Overlay ───
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(28, 27, 28, 0.3); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  z-index: 999; padding: 24px;
}

// ─── Card ───
.modal-card {
  background: $color-organic-surface-container-lowest;
  width: 100%; max-width: 360px;
  border-radius: 24px; overflow: hidden;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.08);
}

// ─── Icon ───
.modal-icon-wrap {
  width: 64px; height: 64px;
  display: flex; align-items: center; justify-content: center;
  margin: 32px auto 24px;
}
// danger: coral organic blob
.icon-danger {
  background: #FFE8E3; color: #F06A58;
  border-radius: 50% 50% 40% 60% / 60% 40% 60% 40%;
}
// warning: error-container/50 + error color
.icon-warning {
  background: rgba(255, 218, 214, 0.5); color: #ba1a1a;
  border-radius: 50%;
}
// info: soft lilac blob
.icon-info {
  background: $color-soft-lilac; color: #4e453c;
  border-radius: 50% 50% 40% 60% / 60% 40% 60% 40%;
}

.modal-icon { font-size: 32px; color: inherit; }

// ─── Title ───
.modal-title {
  display: block; text-align: center;
  font-family: 'Inter', sans-serif; font-size: 24px; font-weight: 600;
  color: $color-organic-on-surface; line-height: 32px;
  margin: 0 32px 12px;
}

// ─── Description ───
.modal-desc {
  display: block; text-align: center;
  font-size: 14px; color: $color-organic-text-secondary;
  line-height: 20px; margin: 0 32px;
}

// ═══════════════════════════════════════════════════
//  Flat Actions (退出登录风格)
//  border-top 分割线 + 左右平铺按钮 + 竖分割线
// ═══════════════════════════════════════════════════
.modal-actions-flat {
  display: flex;
  margin-top: 24px;
  border-top: 1px solid rgba($color-organic-outline-variant, 0.3);
}
.flat-cancel {
  flex: 1; padding: 16px 0; text-align: center;
  &:active { background: rgba($color-organic-surface-variant, 0.4); }
}
.flat-cancel-text {
  font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 400;
  color: $color-organic-text-secondary; line-height: 20px;
}
.flat-divider {
  width: 1px; background: rgba($color-organic-outline-variant, 0.3);
}
.flat-confirm {
  flex: 1; padding: 16px 0; text-align: center;
  &:active { opacity: 0.8; }
}
.flat-confirm-text {
  font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 500;
  line-height: 20px;
}
// warning flat confirm: secondary-container green
.flat-confirm-warning .flat-confirm-text {
  color: $color-organic-secondary;
}
// danger flat confirm: error red
.flat-confirm-danger .flat-confirm-text {
  color: $color-error;
}
// info flat confirm: primary black
.flat-confirm-info .flat-confirm-text {
  color: $color-organic-primary;
}

// ═══════════════════════════════════════════════════
//  Rounded Actions (删除风格)
//  圆角胶囊按钮 + gap
// ═══════════════════════════════════════════════════
.modal-actions-rounded {
  display: flex; gap: 12px;
  padding: 24px 24px 28px; width: 100%; box-sizing: border-box;
}

.rounded-cancel {
  flex: 1; padding: 14px 0; border-radius: 16px;
  background: $color-organic-surface-container; text-align: center;
  transition: all 0.15s;
  &:active { transform: scale(0.97); background: $color-organic-surface-container-high; }
}
.rounded-cancel-text {
  font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 500;
  color: $color-organic-on-surface;
}

.rounded-confirm {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 14px 0; border-radius: 16px;
  transition: all 0.15s;
  &:active { transform: scale(0.97); opacity: 0.9; }
}
.rounded-confirm-icon { font-size: 18px; color: #fff; line-height: 1; }
.rounded-confirm-text {
  font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 500; color: #fff;
  line-height: 20px;
}

// danger: coral #FF8575
.rounded-confirm-danger {
  background: #FF8575;
  box-shadow: 0 4px 12px rgba(255, 133, 117, 0.3);
}
// warning: dark green
.rounded-confirm-warning {
  background: $color-dark-green;
  box-shadow: 0 4px 12px rgba(29, 59, 22, 0.2);
}
// info: black
.rounded-confirm-info {
  background: $color-organic-primary;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
