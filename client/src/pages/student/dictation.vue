<template>
  <view class="page">
    <!-- Task Header -->
    <view class="task-header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="close-btn" @tap="handleClose">
        <text class="material-symbols-outlined">close</text>
      </view>
      <view class="progress-bar-wrap">
        <view class="progress-bar-bg">
          <view class="progress-bar-fill" :style="{ width: progressPct + '%' }">
            <view class="progress-sparkle"></view>
          </view>
        </view>
        <text class="progress-text">{{ progressLabel }}</text>
      </view>
    </view>

    <!-- Main -->
    <view class="main" :style="{ paddingTop: (statusBarHeight + 60) + 'px' }">
      <!-- Intro Badge -->
      <view class="intro-badge">
        <text class="intro-star">⭐</text>
        <text class="intro-text">请准备好你的作业本，听写开始啦！</text>
      </view>

      <!-- Giant Play Button -->
      <view class="play-btn-wrap">
        <view class="play-ripple"></view>
        <view :class="['play-btn', tts.isPlaying.value ? 'play-btn-playing' : '']" @tap="handlePlay">
          <text class="material-symbols-outlined play-icon">{{ tts.isPlaying.value ? 'pause' : 'play_arrow' }}</text>
        </view>
      </view>

      <!-- Instruction -->
      <view class="instruction-wrap">
        <text class="instruction-text">认真听发音，并在</text>
        <view class="instruction-highlight-wrap">
          <text class="instruction-highlight">作业本</text>
          <view class="underline-wave">
            <svg width="60" height="8" viewBox="0 0 60 8" fill="none">
              <path d="M0,4 Q30,8 60,4" stroke="#edc157" stroke-width="3" fill="none"/>
            </svg>
          </view>
        </view>
        <text class="instruction-text">上手写</text>
      </view>

      <!-- Reveal Hint Area -->
      <view class="reveal-area" @tap="toggleReveal">
        <view class="reveal-hint-row">
          <text class="material-symbols-outlined reveal-icon">volume_up</text>
          <text class="reveal-hint">点击再次播放或查看提示</text>
        </view>
        <view :class="['reveal-word', revealHint ? '' : 'reveal-word-blur']">
          <text class="reveal-word-text">{{ currentWord || '...' }}</text>
        </view>
      </view>
    </view>

    <!-- Bottom Action -->
    <view class="bottom-action" :style="{ paddingBottom: (safeAreaBottom + 16) + 'px' }">
      <view class="check-btn" @tap="handleFinish">
        <text class="check-btn-text">检查答案</text>
        <text class="material-symbols-outlined check-arrow">arrow_forward</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getDictationItems } from '@/api/dictation'
import { useTTS } from '@/composables/useTTS'
import { useTasksStore } from '@/stores/tasks'
import type { DictationItemOut } from '@/api/dictation'

const taskId = ref('')
const items = ref<DictationItemOut[]>([])
const tts = useTTS()
const tasksStore = useTasksStore()
const statusBarHeight = ref(0)
const safeAreaBottom = ref(0)
const revealHint = ref(false)

const currentWord = computed(() => {
  if (tts.currentIndex.value < 0) return ''
  return items.value[tts.currentIndex.value]?.content || ''
})

const progressPct = computed(() => {
  if (items.value.length === 0) return 0
  return Math.round(((tts.currentIndex.value + 1) / items.value.length) * 100)
})

const progressLabel = computed(() => {
  if (items.value.length === 0) return '0/0'
  return `${tts.currentIndex.value + 1}/${items.value.length}`
})

async function loadItems() {
  try {
    items.value = await getDictationItems(taskId.value)
    tts.setWords(items.value.map(i => i.content))
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

function handlePlay() {
  if (tts.isPlaying.value) {
    tts.stop()
  } else {
    const speed = items.value[0]?.speed || 1.0
    const pause = items.value[0]?.pause_interval || 3
    tts.playSequence(speed, pause)
  }
}

function toggleReveal() {
  revealHint.value = !revealHint.value
  if (!tts.isPlaying.value && items.value.length > 0) {
    const speed = items.value[tts.currentIndex.value]?.speed || 1.0
    const pause = items.value[tts.currentIndex.value]?.pause_interval || 3
    tts.playSequence(speed, pause)
  }
}

async function handleFinish() {
  tts.stop()
  if (taskId.value) {
    try {
      await tasksStore.submitTask(taskId.value)
    } catch { /* ignore */ }
  }
  uni.navigateBack()
}

function handleClose() {
  tts.stop()
  uni.navigateBack()
}

onMounted(() => {
  const info = uni.getSystemInfoSync()
  statusBarHeight.value = info.statusBarHeight || 0
  safeAreaBottom.value = info.safeAreaInsets?.bottom || 0
  const pages = getCurrentPages()
  const page = pages[pages.length - 1] as any
  taskId.value = page.$page?.options?.taskId || page.options?.taskId || ''
  if (taskId.value) loadItems()
})

onUnmounted(() => tts.stop())
</script>

<style lang="scss" scoped>
@use '@/static/styles/variables.scss' as *;

.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-weight: normal; font-style: normal; font-size: 24px; line-height: 1;
  letter-spacing: normal; text-transform: none; display: inline-block;
  white-space: nowrap; word-wrap: normal; direction: ltr;
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.page {
  min-height: 100vh; background: $color-surface;
  font-family: $font-family-body; display: flex; flex-direction: column;
}

// Header
.task-header {
  position: fixed; top: 0; left: 0; right: 0; z-index: 10;
  background: rgba($color-surface, 0.9); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: space-between;
  padding-left: $spacing-margin; padding-right: $spacing-margin; padding-bottom: $spacing-md;
}
.close-btn {
  width: 48px; height: 48px; border-radius: $radius-full;
  background: $color-surface-container; display: flex; align-items: center; justify-content: center;
  color: $color-on-surface-variant; flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}
.progress-bar-wrap {
  flex: 1; margin: 0 $spacing-margin; display: flex; align-items: center; gap: $spacing-sm;
}
.progress-bar-bg {
  flex: 1; height: 16px; background: $color-surface-container-highest;
  border-radius: $radius-full; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.06);
}
.progress-bar-fill {
  height: 100%; background: $color-tertiary-container; border-radius: $radius-full;
  position: relative; transition: width 0.3s;
}
.progress-sparkle {
  position: absolute; inset: 0; background: rgba(255,255,255,0.2);
  width: 50%; transform: skewX(-20deg);
}
.progress-text {
  font-family: $font-family; font-size: $font-label-md; font-weight: 600;
  color: $color-on-surface-variant; min-width: 36px; text-align: right;
}

// Main
.main {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  padding-left: $spacing-margin; padding-right: $spacing-margin;
  padding-bottom: 140px;
}

// Intro badge
.intro-badge {
  display: flex; align-items: center; gap: $spacing-base;
  padding: $spacing-sm $spacing-md; background: $color-surface-container-low;
  border-radius: $radius-full; border: 1px solid $color-surface-container;
  margin-bottom: $spacing-xl; box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}
.intro-star { font-size: 20px; }
.intro-text { font-size: $font-body-md; color: $color-on-surface-variant; }

// Play button
.play-btn-wrap {
  position: relative; margin-bottom: $spacing-xl;
}
.play-ripple {
  position: absolute; inset: 0; border-radius: $radius-full;
  background: $color-primary-fixed; transform: scale(1.1); opacity: 0.5;
}
.play-btn {
  position: relative; width: 180px; height: 180px; border-radius: $radius-full;
  background: $color-primary; display: flex; align-items: center; justify-content: center;
  border-bottom: 8px solid $color-on-primary-fixed-variant;
  box-shadow: 0 8px 24px rgba(0, 88, 189, 0.25); z-index: 1;
  &:active { border-bottom-width: 0; transform: translateY(8px); }
}
.play-icon { font-size: 100px; color: $color-on-primary; margin-left: 8px; }

// Instruction
.instruction-wrap {
  display: flex; align-items: center; flex-wrap: wrap; justify-content: center;
  margin-bottom: $spacing-xl; max-width: 280px; text-align: center;
}
.instruction-text { font-family: $font-family; font-size: $font-headline-lg; font-weight: 600; color: $color-on-surface; }
.instruction-highlight-wrap { position: relative; display: inline-block; margin: 0 4px; }
.instruction-highlight { font-family: $font-family; font-size: $font-headline-lg; font-weight: 600; color: $color-primary; }
.underline-wave { position: absolute; bottom: -8px; left: 0; right: 0; display: flex; justify-content: center; }

// Reveal area
.reveal-area {
  width: 100%; max-width: 320px; background: $color-surface-container;
  border-radius: $radius-xl; padding: $spacing-md;
  border: 2px dashed $color-outline-variant;
  display: flex; flex-direction: column; align-items: center; gap: $spacing-base;
  margin-top: auto;
}
.reveal-hint-row { display: flex; align-items: center; gap: $spacing-base; color: $color-on-surface-variant; }
.reveal-icon { font-size: 20px; }
.reveal-hint { font-family: $font-family; font-size: $font-label-sm; }
.reveal-word {
  background: #fff; border-radius: $radius-lg; padding: $spacing-base $spacing-xl;
  width: 100%; text-align: center; border: 1px solid $color-surface-container-high;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04); transition: filter 0.3s;
}
.reveal-word-blur { filter: blur(4px); opacity: 0.7; }
.reveal-word-text { font-family: $font-family; font-size: 32px; font-weight: 700; color: $color-on-surface; letter-spacing: 0.1em; }

// Bottom action
.bottom-action {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 20;
  padding-left: $spacing-margin; padding-right: $spacing-margin; padding-top: $spacing-xl;
  background: linear-gradient(to top, $color-surface 60%, transparent);
}
.check-btn {
  display: flex; align-items: center; justify-content: center; gap: $spacing-md;
  background: $color-tertiary-container; color: $color-on-tertiary-container;
  padding: 18px; border-radius: $radius-xl;
  border-bottom: 6px solid $color-on-tertiary-fixed-variant;
  font-family: $font-family; font-size: $font-headline-lg; font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 131, 121, 0.2);
  &:active { border-bottom-width: 0; transform: translateY(6px); }
}
.check-btn-text { color: $color-on-tertiary-container; }
.check-arrow { font-size: 28px; font-variation-settings: 'wght' 600; color: $color-on-tertiary-container; }
</style>
