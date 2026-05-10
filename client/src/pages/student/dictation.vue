<template>
  <view class="dictation-page">
    <view v-if="items.length === 0" class="empty">
      <text class="empty-text">该任务没有听写内容</text>
    </view>

    <view v-else class="dictation-content">
      <text class="word-display">{{ currentWord || '准备开始' }}</text>
      <text class="progress">{{ tts.currentIndex.value + 1 }} / {{ items.length }}</text>

      <view class="controls">
        <button class="ctrl-btn" @tap="handlePlay">{{ tts.isPlaying.value ? '暂停' : '开始' }}</button>
        <button class="ctrl-btn" @tap="handleReplay">重播</button>
        <button class="ctrl-btn" @tap="handleSkip">下一个</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getDictationItems } from '@/api/dictation'
import { useTTS } from '@/composables/useTTS'
import type { DictationItemOut } from '@/api/dictation'

const taskId = ref('')
const items = ref<DictationItemOut[]>([])
const tts = useTTS()

const currentWord = computed(() => {
  if (tts.currentIndex.value < 0) return ''
  return items.value[tts.currentIndex.value]?.content || ''
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

function handleReplay() {
  tts.stop()
  setTimeout(() => {
    const speed = items.value[0]?.speed || 1.0
    const pause = items.value[0]?.pause_interval || 3
    tts.playSequence(speed, pause)
  }, 300)
}

function handleSkip() {
  tts.skipNext()
}

onMounted(() => {
  const pages = getCurrentPages()
  const page = pages[pages.length - 1] as any
  taskId.value = page.$page?.options?.taskId || page.options?.taskId || ''
  if (taskId.value) loadItems()
})

onUnmounted(() => tts.stop())
</script>

<style lang="scss" scoped>
@import '@/static/styles/variables.scss';

.dictation-page {
  min-height: 100vh; display: flex; flex-direction: column;
  align-items: center; justify-content: center; padding: $spacing-lg;
}

.word-display {
  font-size: 48px; font-weight: 500; color: $color-primary-light;
  letter-spacing: 0.05em; line-height: 1.5; text-align: center;
}

.progress {
  font-size: $font-body-lg; color: $color-on-surface-variant;
  margin-top: $spacing-md; margin-bottom: $spacing-lg;
}

.controls { display: flex; gap: $spacing-sm; }
.ctrl-btn {
  min-width: 80px; height: $touch-min; border-radius: $radius-md;
  font-size: $font-body-md; font-weight: 600; border: none;
  background: $color-primary; color: #fff;
}

.empty { text-align: center; }
.empty-text { font-size: $font-body-lg; color: $color-on-surface-variant; }
</style>
