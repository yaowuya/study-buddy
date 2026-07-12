<template>
  <view class="page">
    <!-- Immersive Background blobs -->
    <view class="bg-blobs">
      <view class="blob blob-1"></view>
      <view class="blob blob-2"></view>
      <view class="blob blob-3"></view>
    </view>

    <!-- Sticky Progress Bar -->
    <view class="progress-header" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="progress-bar-row">
        <view class="progress-track">
          <view class="progress-fill" :style="{ width: progressPct + '%' }"></view>
        </view>
        <text class="progress-label">{{ progressLabel }}</text>
      </view>
    </view>

    <scroll-view scroll-y class="main" :style="{ paddingTop: (statusBarHeight + 60) + 'px' }">
      <!-- Header: back + title (scrolls with content) -->
      <view class="appbar">
        <view class="appbar-back" @tap="handleClose">
          <text class="material-symbols-outlined">arrow_back</text>
        </view>
        <text class="appbar-title">听写闯关</text>
        <view class="appbar-spacer"></view>
      </view>

      <!-- Motivational Message Card -->
      <view class="motivation-card">
        <view class="motivation-avatar">
          <text class="material-symbols-outlined motivation-icon">face_6</text>
        </view>
        <view class="motivation-text">
          <text class="motivation-title">{{ motivationTitle }}</text>
          <text class="motivation-sub">{{ motivationSub }}</text>
        </view>
        <view class="motivation-deco"></view>
      </view>

      <!-- Main Playback Cloud -->
      <view v-if="!allPlayed" class="playback-cloud">
        <view class="playback-status">
          <view class="playback-status-badge">
            <text class="playback-status-text">{{ currentIndex >= 0 ? '正在朗读...' : '准备好了吗？' }}</text>
          </view>
          <text class="playback-word-number">{{ dictationPositionLabel(currentIndex, nextUnplayedIndex) }}</text>
        </view>

        <!-- Bouncy Playback Button -->
        <view :class="['playback-btn', isPlaying ? 'playback-btn-playing' : '']" @tap="handlePlaybackTap">
          <text class="material-symbols-outlined playback-btn-icon">
            {{ isPlaying ? 'cruelty_free' : 'volume_up' }}
          </text>
          <text class="playback-btn-label">{{ isPlaying ? '朗读中...' : '点击朗读' }}</text>
        </view>

        <!-- Slow play button -->
        <view class="slow-play-btn" @tap="playSlowCurrent">
          <text class="slow-play-text">慢速播放</text>
        </view>
      </view>

      <!-- Upcoming Word List -->
      <view class="word-list-card">
        <view class="word-list-header">
          <text class="word-list-title">听写清单</text>
          <text class="word-list-count">共 {{ words.length }} 个词</text>
        </view>
        <view class="word-list">
          <view
            v-for="(word, i) in words"
            :key="i"
            :class="[
              'word-item',
              playedWords[i] ? 'word-item-played' : '',
              currentIndex === i ? 'word-item-current' : '',
              showAnswers ? 'word-item-revealed' : '',
            ]"
            @tap="playSingleWord(i)"
          >
            <view class="word-item-left">
              <view :class="['word-num', playedWords[i] ? 'word-num-done' : '', currentIndex === i ? 'word-num-active' : '']">
                <text class="word-num-text">{{ i + 1 }}</text>
              </view>
              <text v-if="showAnswers" class="word-item-text">{{ word }}</text>
              <text v-else-if="playedWords[i]" class="word-item-pending">已听写</text>
              <text v-else class="word-item-pending">{{ currentIndex === i ? '正在听写' : '待听写' }}</text>
            </view>
            <text v-if="!playedWords[i] && currentIndex !== i" class="material-symbols-outlined word-lock">lock</text>
            <text v-else-if="playedWords[i]" class="material-symbols-outlined word-check">check_circle</text>
            <text v-else class="material-symbols-outlined word-playing-icon">volume_up</text>
          </view>
        </view>
      </view>

      <view class="bottom-spacer"></view>
    </scroll-view>

    <!-- Floating Primary Action -->
    <view class="bottom-action" :style="{ paddingBottom: (safeAreaBottom + 16) + 'px' }">
      <view v-if="!allPlayed" class="action-btn" @tap="startDictation">
        <text class="material-symbols-outlined action-icon">play_arrow</text>
        <text class="action-text">{{ hasPlayedAny ? '继续听写' : '开始听写' }}</text>
      </view>
      <view v-else-if="!showAnswers" class="action-btn action-btn-check" @tap="showAnswersAction">
        <text class="material-symbols-outlined action-icon">visibility</text>
        <text class="action-text">查看答案</text>
      </view>
      <view v-else-if="isContinuousMode && hasNextTask" class="action-btn" @tap="nextTask">
        <text class="material-symbols-outlined action-icon">arrow_forward</text>
        <text class="action-text">下一个听写任务</text>
      </view>
      <view v-else class="action-btn action-btn-back" @tap="handleClose">
        <text class="material-symbols-outlined action-icon">arrow_back</text>
        <text class="action-text">返回</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, onUnmounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getDictationItems } from '@/api/dictation'
import { useTasksStore } from '@/stores/tasks'
import type { DictationItemOut } from '@/api/dictation'
import { BASE_URL } from '@/api/config'
import { getTask } from '@/api/tasks'
import { dictationPositionLabel } from '@/utils/dictation-progress'
import { shouldStartDictationTask } from '@/utils/dictation-task-status'

const taskId = ref('')
const taskIds = ref<string[]>([])
const taskTitles = ref<string[]>([])
const currentTaskIndex = ref(0)
const isContinuousMode = ref(false)
const taskTitle = ref('')
const items = ref<DictationItemOut[]>([])
const tasksStore = useTasksStore()
const statusBarHeight = ref(0)
const safeAreaBottom = ref(0)
const playedWords = reactive<Record<number, boolean>>({})
const showAnswers = ref(false)
const currentIndex = ref(-1)
const isPlaying = ref(false)
const autoPlayTimer = ref<ReturnType<typeof setTimeout> | null>(null)
const ttsReady = ref(false)
const stopSpeaking = ref(false)

const words = computed(() => items.value.map(i => i.content))

const nextUnplayedIndex = computed(() => {
  return words.value.findIndex((_, i) => !playedWords[i])
})

const allPlayed = computed(() => {
  if (words.value.length === 0) return false
  return words.value.every((_, i) => playedWords[i])
})

const hasPlayedAny = computed(() => {
  return Object.values(playedWords).some(Boolean)
})

const hasNextTask = computed(() => {
  return isContinuousMode.value && currentTaskIndex.value < taskIds.value.length - 1
})

const progressPct = computed(() => {
  if (words.value.length === 0) return 0
  const playedCount = Object.values(playedWords).filter(Boolean).length
  return Math.round((playedCount / words.value.length) * 100)
})

const progressLabel = computed(() => {
  if (words.value.length === 0) return '0/0'
  const playedCount = Object.values(playedWords).filter(Boolean).length
  return `${playedCount}/${words.value.length}`
})

const motivationTitle = computed(() => {
  if (allPlayed.value) return '太棒了！全部完成！'
  if (hasPlayedAny.value) return '加油，小勇士！'
  return '加油，小勇士！'
})

const motivationSub = computed(() => {
  if (allPlayed.value) return '你已经听写了所有词语！'
  if (hasPlayedAny.value) return '准备好听写下一个词语了吗？'
  return '请准备好你的作业本，听写开始啦！'
})

async function loadItems() {
  try {
    items.value = await getDictationItems(taskId.value)
    if (taskId.value) {
      const task = await getTask(taskId.value)
      if (shouldStartDictationTask(task.status)) {
        await tasksStore.updateStatus(taskId.value, 'in_progress')
      }
      taskTitle.value = task.title
    }
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

let dictationAudioContext: UniApp.InnerAudioContext | null = null

function getTTSAudioUrl(text: string, rate: number = 1.0): string {
  return `${BASE_URL}/tts/speak?text=${encodeURIComponent(text)}&rate=${rate}`
}

function speak(text: string, rate: number = 1.0): Promise<void> {
  return new Promise((resolve) => {
    if (stopSpeaking.value) {
      resolve()
      return
    }

    try {
      if (dictationAudioContext) {
        dictationAudioContext.destroy()
      }

      dictationAudioContext = uni.createInnerAudioContext()
      dictationAudioContext.volume = 1.0
      dictationAudioContext.src = getTTSAudioUrl(text, rate)

      dictationAudioContext.onCanplay(() => {
        dictationAudioContext?.play()
      })

      dictationAudioContext.onEnded(() => {
        dictationAudioContext?.destroy()
        dictationAudioContext = null
        resolve()
      })

      dictationAudioContext.onError((e) => {
        dictationAudioContext?.destroy()
        dictationAudioContext = null
        resolve()
      })
    } catch (e) {
      resolve()
    }
  })
}

async function speakMultiple(text: string, times: number = 3, pauseMs: number = 800): Promise<void> {
  for (let i = 0; i < times; i++) {
    if (stopSpeaking.value) return
    await speak(text)
    if (stopSpeaking.value) return
    if (i < times - 1) {
      await delay(pauseMs)
    }
  }
}

function delay(ms: number): Promise<void> {
  return new Promise(resolve => {
    const startTime = Date.now()
    const checkInterval = setInterval(() => {
      if (stopSpeaking.value || Date.now() - startTime >= ms) {
        clearInterval(checkInterval)
        resolve()
      }
    }, 50)
  })
}

function initTTS(): Promise<void> {
  return new Promise((resolve) => {
    // #ifdef H5
    const voices = speechSynthesis.getVoices()
    if (voices.length > 0) {
      warmUpTTS()
      ttsReady.value = true
      resolve()
    } else {
      speechSynthesis.onvoiceschanged = () => {
        warmUpTTS()
        ttsReady.value = true
        resolve()
      }
      setTimeout(() => {
        warmUpTTS()
        ttsReady.value = true
        resolve()
      }, 200)
    }
    // #endif

    // #ifdef APP-PLUS
    ttsReady.value = true
    resolve()
    // #endif
  })
}

function warmUpTTS(): Promise<void> {
  return new Promise((resolve) => {
    // #ifdef H5
    speechSynthesis.cancel()
    const warmUp = new SpeechSynthesisUtterance('嗯')
    warmUp.lang = 'zh-CN'
    warmUp.rate = 10
    warmUp.volume = 0.01
    warmUp.onend = () => resolve()
    warmUp.onerror = () => resolve()
    speechSynthesis.speak(warmUp)
    setTimeout(resolve, 100)
    // #endif

    // #ifdef APP-PLUS
    resolve()
    // #endif
  })
}

function clearAutoPlayTimer() {
  if (autoPlayTimer.value) {
    clearTimeout(autoPlayTimer.value)
    autoPlayTimer.value = null
  }
}

async function playWord(index: number) {
  if (index >= words.value.length) {
    isPlaying.value = false
    currentIndex.value = -1
    return
  }

  resumeSpeech()
  currentIndex.value = index
  await speakMultiple(words.value[index], 3)
  playedWords[index] = true

  if (isPlaying.value && index + 1 < words.value.length) {
    autoPlayTimer.value = setTimeout(() => {
      if (isPlaying.value) {
        playWord(index + 1)
      }
    }, 5000)
  } else {
    isPlaying.value = false
    currentIndex.value = -1
  }
}

async function playSingleWord(index: number) {
  if (currentIndex.value === index) return

  stopSpeech()
  clearAutoPlayTimer()
  await delay(150)
  isPlaying.value = false

  if (!ttsReady.value) {
    await initTTS()
  }

  resumeSpeech()
  currentIndex.value = index
  await speakMultiple(words.value[index], 3)
  playedWords[index] = true
  currentIndex.value = -1
}

// Play current word slowly
async function playSlowCurrent() {
  const idx = currentIndex.value >= 0 ? currentIndex.value : nextUnplayedIndex.value
  if (idx < 0) return

  stopSpeech()
  clearAutoPlayTimer()
  await delay(150)
  isPlaying.value = false

  if (!ttsReady.value) {
    await initTTS()
  }

  resumeSpeech()
  currentIndex.value = idx
  await speak(words.value[idx], 0.5)
  await delay(500)
  await speak(words.value[idx], 0.5)
  playedWords[idx] = true
  currentIndex.value = -1
}

function handlePlaybackTap() {
  if (isPlaying.value) {
    // Currently playing, do nothing (user should use word list to interact)
    return
  }
  // Start playing from next unplayed word
  startDictation()
}

async function startDictation() {
  if (allPlayed.value) return

  if (!ttsReady.value) {
    uni.showToast({ title: '正在初始化语音...', icon: 'none' })
    await initTTS()
  }

  await warmUpTTS()

  isPlaying.value = true
  const startIndex = words.value.findIndex((_, i) => !playedWords[i])

  if (startIndex >= 0) {
    playWord(startIndex)
  }
}

function pauseDictation() {
  isPlaying.value = false
  clearAutoPlayTimer()
  stopSpeech()
}

function showAnswersAction() {
  showAnswers.value = true
}

async function nextTask() {
  if (!hasNextTask.value) return

  currentTaskIndex.value++
  taskId.value = taskIds.value[currentTaskIndex.value]

  Object.keys(playedWords).forEach(key => delete playedWords[Number(key)])
  showAnswers.value = false
  currentIndex.value = -1
  isPlaying.value = false
  clearAutoPlayTimer()

  await loadItems()
}

function handleClose() {
  isPlaying.value = false
  clearAutoPlayTimer()
  stopSpeech()
  uni.navigateBack()
}

function stopSpeech() {
  stopSpeaking.value = true
  try {
    if (dictationAudioContext) {
      dictationAudioContext.stop()
      dictationAudioContext.destroy()
      dictationAudioContext = null
    }
  } catch {}
}

function resumeSpeech() {
  stopSpeaking.value = false
}

onLoad(async (query) => {
  if (query?.taskIds && query?.continuous === '1') {
    isContinuousMode.value = true
    taskIds.value = query.taskIds.split(',')
    currentTaskIndex.value = 0
    taskId.value = taskIds.value[0]
  } else {
    taskId.value = query?.taskId || ''
  }

  if (taskId.value) loadItems()
  await initTTS()
})

onMounted(() => {
  const info = uni.getSystemInfoSync()
  statusBarHeight.value = info.statusBarHeight || 0
  safeAreaBottom.value = info.safeAreaInsets?.bottom || 0
})

onUnmounted(() => {
  isPlaying.value = false
  clearAutoPlayTimer()
  stopSpeech()
})
</script>

<style lang="scss" scoped>
@use '@/static/styles/variables.scss' as *;

.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-weight: normal; font-style: normal; line-height: 1;
  letter-spacing: normal; text-transform: none; display: inline-block;
  white-space: nowrap; word-wrap: normal; direction: ltr;
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.page {
  min-height: 100vh; background: #f8fbf8;
  font-family: 'Inter', sans-serif; position: relative;
}

// ═══════════════════════════════════════════════════
// Immersive Background Blobs
// ═══════════════════════════════════════════════════
.bg-blobs {
  position: fixed; inset: 0; pointer-events: none; overflow: hidden; z-index: 0;
}
.blob {
  position: absolute; border-radius: 50%; filter: blur(60px);
}
.blob-1 { top: -80px; left: -80px; width: 256px; height: 256px; background: rgba($color-mint-green, 0.3); }
.blob-2 { top: 50%; right: -128px; width: 320px; height: 320px; background: rgba($color-mint-green-bright, 0.4); }
.blob-3 { bottom: -80px; left: 25%; width: 288px; height: 288px; background: rgba($color-mint-green-dim, 0.2); }

// ═══════════════════════════════════════════════════
// Sticky Progress Bar
// ═══════════════════════════════════════════════════
.progress-header {
  position: fixed; top: 0; left: 0; right: 0; z-index: 50;
  background: rgba(252, 248, 248, 0.8); backdrop-filter: blur(12px);
  padding-left: $spacing-margin; padding-right: $spacing-margin; padding-bottom: 12px;
  border-bottom: 1px solid rgba($color-organic-surface-variant, 0.3);
}
.progress-bar-row {
  display: flex; align-items: center; gap: 12px;
}
.progress-track {
  flex: 1; height: 12px; background: $color-organic-surface-container-high;
  border-radius: $radius-full; overflow: hidden;
}
.progress-fill {
  height: 100%; background: $color-organic-secondary;
  border-radius: $radius-full; transition: width 0.7s ease;
}
.progress-label {
  font-size: 16px; font-weight: 700; color: $color-on-secondary-fixed-variant;
  letter-spacing: -0.02em; min-width: 36px; text-align: right;
}

// ═══════════════════════════════════════════════════
// AppBar
// ═══════════════════════════════════════════════════
.appbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 0 16px 0;
}
.appbar-back {
  width: 40px; height: 40px; border-radius: $radius-full;
  background: rgba(255, 255, 255, 0.8); display: flex; align-items: center; justify-content: center;
  color: $color-organic-on-surface-variant; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  &:active { transform: scale(0.9); }
}
.appbar-back .material-symbols-outlined { font-size: 20px; color: $color-organic-on-surface-variant; }
.appbar-title {
  font-size: 18px; font-weight: 500; color: $color-organic-primary;
}
.appbar-spacer { width: 40px; }

// ═══════════════════════════════════════════════════
// Main
// ═══════════════════════════════════════════════════
.main {
  flex: 1; padding: 0 $spacing-margin; box-sizing: border-box; width: 100%;
  padding-bottom: 140px; position: relative; z-index: 1;
}

// ═══════════════════════════════════════════════════
// Motivational Card (mint-green cloud)
// ═══════════════════════════════════════════════════
.motivation-card {
  background: rgba($color-mint-green-bright, 0.4);
  border-radius: 48px; padding: 24px;
  display: flex; align-items: center; gap: 16px;
  filter: drop-shadow(0 10px 20px rgba(0,0,0,0.05));
  position: relative; overflow: hidden; margin-bottom: 24px;
}
.motivation-avatar {
  width: 56px; height: 56px; background: rgba(255, 255, 255, 0.6);
  border-radius: $radius-full; padding: 8px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.motivation-icon {
  font-size: 40px; color: $color-organic-on-secondary-container;
  animation: bounce-subtle 3s ease-in-out infinite;
}
@keyframes bounce-subtle {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
.motivation-text { display: flex; flex-direction: column; }
.motivation-title { font-size: 18px; font-weight: 500; color: $color-organic-primary; }
.motivation-sub { font-size: 14px; color: $color-on-secondary-fixed-variant; margin-top: 2px; }
.motivation-deco {
  position: absolute; right: -16px; bottom: -16px;
  width: 48px; height: 48px; background: rgba(255, 255, 255, 0.3);
  border-radius: $radius-full;
}

// ═══════════════════════════════════════════════════
// Main Playback Cloud (cloud-shape)
// ═══════════════════════════════════════════════════
.playback-cloud {
  background: rgba($color-mint-green, 0.5);
  border-radius: 60% 40% 70% 30% / 40% 50% 60% 50%;
  padding: 40px 32px;
  display: flex; flex-direction: column; align-items: center; gap: 32px;
  filter: drop-shadow(0 10px 20px rgba(0,0,0,0.05));
  border: 4px solid rgba(255, 255, 255, 0.8);
  margin-bottom: 24px;
}
.playback-status {
  text-align: center; display: flex; flex-direction: column; align-items: center; gap: 8px;
}
.playback-status-badge {
  display: inline-block; padding: 4px 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: $radius-full;
}
.playback-status-text {
  font-size: 12px; font-weight: 700; color: $color-organic-on-secondary-container;
}
.playback-word-number {
  font-size: 36px; font-weight: 700; color: $color-organic-primary;
  letter-spacing: -0.02em; line-height: 44px;
}

// Bouncy Playback Button
.playback-btn {
  width: 128px; height: 128px; border-radius: $radius-full;
  background: rgba(255, 255, 255, 0.9);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 8px 0 rgba(0,0,0,0.1);
  &:active {
    transform: scale(0.9) translateY(4px);
    box-shadow: 0 2px 0 rgba(0,0,0,0.1);
  }
}
.playback-btn-playing {
  animation: pulse-glow 2s ease-in-out infinite;
}
@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 8px 0 rgba(0,0,0,0.1), 0 0 0 0 rgba($color-mint-green, 0.4); }
  50% { box-shadow: 0 8px 0 rgba(0,0,0,0.1), 0 0 0 16px rgba($color-mint-green, 0); }
}
.playback-btn-icon {
  font-size: 60px; color: $color-organic-on-secondary-container;
}
.playback-btn-label {
  font-size: 12px; font-weight: 700; color: $color-organic-on-secondary-container;
  margin-top: 4px;
}

// Slow play button
.slow-play-btn {
  padding: 8px 24px; background: rgba(255, 255, 255, 0.8);
  border-radius: $radius-full;
  &:active { transform: scale(0.95); }
}
.slow-play-text {
  font-size: 14px; font-weight: 500; color: $color-organic-on-secondary-container;
}

// ═══════════════════════════════════════════════════
// Word List Card (upcoming list)
// ═══════════════════════════════════════════════════
.word-list-card {
  background: rgba($color-mint-green-bright, 0.2);
  border-radius: 40px; padding: 24px;
  display: flex; flex-direction: column; gap: 16px;
  border: 1px solid rgba(255, 255, 255, 0.5);
}
.word-list-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 8px;
}
.word-list-title { font-size: 18px; font-weight: 500; color: $color-on-secondary-fixed-variant; }
.word-list-count { font-size: 12px; color: $color-on-secondary-fixed-variant; opacity: 0.7; }

.word-list { display: flex; flex-direction: column; gap: 12px; }

.word-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px; background: rgba(255, 255, 255, 0.9);
  border-radius: 16px; border: 1px solid #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  transition: all 0.15s;
  &:active { transform: scale(0.98); }
}
.word-item-played {
  background: rgba(255, 255, 255, 0.5);
  border-color: rgba(255, 255, 255, 0.5);
}
.word-item-current {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba($color-mint-green, 0.5);
}
.word-item-revealed {
  background: rgba(255, 255, 255, 0.9);
}

.word-item-left { display: flex; align-items: center; gap: 12px; }
.word-num {
  width: 32px; height: 32px; border-radius: $radius-full;
  background: $color-mint-green; display: flex; align-items: center; justify-content: center;
}
.word-num-done { background: rgba($color-mint-green, 0.5); }
.word-num-active { background: $color-mint-green; }
.word-num-text { font-size: 12px; font-weight: 700; color: $color-organic-on-secondary-container; }
.word-num-done .word-num-text { opacity: 0.7; }

.word-item-text { font-size: 14px; color: $color-organic-on-surface-variant; font-weight: 500; }
.word-item-pending { font-size: 14px; color: $color-organic-on-surface-variant; }

.word-lock { font-size: 18px; color: $color-organic-surface-variant; }
.word-check { font-size: 20px; color: $color-dark-green; }
.word-playing-icon { font-size: 18px; color: $color-organic-secondary; }

// ═══════════════════════════════════════════════════
// Bottom Floating Action
// ═══════════════════════════════════════════════════
.bottom-action {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 40;
  padding: 24px $spacing-margin;
  background: linear-gradient(to top, #f8fbf8 70%, transparent);
}
.action-btn {
  width: 100%; height: 64px;
  background: $color-mint-green; color: $color-organic-on-secondary-container;
  border-radius: $radius-full;
  display: flex; align-items: center; justify-content: center; gap: 12px;
  font-size: 24px; font-weight: 600;
  box-shadow: 0 8px 20px rgba($color-mint-green, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.2s;
  &:active {
    transform: scale(0.9) translateY(4px);
    box-shadow: 0 2px 0 rgba(0,0,0,0.1);
  }
}
.action-btn-check {
  background: $color-dark-green; color: #fff;
  box-shadow: 0 8px 20px rgba($color-dark-green, 0.3);
}
.action-btn-back {
  background: $color-organic-primary; color: #fff;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}
.action-icon { font-size: 28px; }
.action-text { color: inherit; }

.bottom-spacer { height: 120px; }
</style>
