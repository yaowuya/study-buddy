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
    <view class="main" :style="{ paddingTop: (statusBarHeight + 100) + 'px' }">
      <!-- Intro Badge -->
      <view class="intro-badge">
        <text class="intro-star">⭐</text>
        <text class="intro-text">请准备好你的作业本，听写开始啦！</text>
      </view>

      <!-- Task Info (Continuous Mode) -->
      <view v-if="isContinuousMode && taskTitles.length > 1" class="task-info">
        <text class="task-info-text">任务 {{ currentTaskIndex + 1 }}/{{ taskIds.length }}</text>
      </view>

      <!-- Word List -->
      <view class="word-list-section">
        <text class="section-title">听写词语</text>
        <text v-if="taskTitle" class="task-title-display">{{ taskTitle }}</text>
        <view class="word-list">
          <view
            v-for="(word, i) in words"
            :key="i"
            :class="['word-item', playedWords[i] ? 'word-item-played' : '', currentIndex === i ? 'word-item-playing' : '']"
            @tap="playSingleWord(i)"
          >
            <view class="word-left">
              <view :class="['play-btn', playedWords[i] ? 'play-btn-done' : '', currentIndex === i ? 'play-btn-active' : '']">
                <text class="material-symbols-outlined play-icon">
                  {{ currentIndex === i ? 'volume_up' : (playedWords[i] ? 'check' : 'play_arrow') }}
                </text>
              </view>
              <text v-if="!showAnswers" class="word-number">第 {{ i + 1 }} 个词</text>
              <text v-else class="word-text">{{ word }}</text>
            </view>
            <view v-if="!playedWords[i]" class="tap-hint">
              <text class="tap-hint-text">点击播放</text>
            </view>
            <text v-else-if="!showAnswers" class="material-symbols-outlined status-icon">check_circle</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Bottom Action -->
    <view class="bottom-action" :style="{ paddingBottom: (safeAreaBottom + 16) + 'px' }">
      <view v-if="!allPlayed" class="action-btn-row">
        <view v-if="!isPlaying" class="action-btn btn-start" @tap="startDictation">
          <text class="material-symbols-outlined btn-icon">play_arrow</text>
          <text class="action-btn-text">{{ hasPlayedAny ? '继续' : '开始听写' }}</text>
        </view>
        <view v-else class="action-btn btn-playing" @tap="pauseDictation">
          <text class="material-symbols-outlined btn-icon">pause</text>
          <text class="action-btn-text">暂停</text>
        </view>
      </view>
      <view v-else-if="!showAnswers" class="check-btn" @tap="showAnswersAction">
        <text class="check-btn-text">检查答案</text>
        <text class="material-symbols-outlined check-arrow">arrow_forward</text>
      </view>
      <view v-else-if="isContinuousMode && hasNextTask" class="check-btn" @tap="nextTask">
        <text class="check-btn-text">下一个听写任务</text>
        <text class="material-symbols-outlined check-arrow">arrow_forward</text>
      </view>
      <view v-else class="check-btn check-btn-back" @tap="handleClose">
        <text class="material-symbols-outlined check-arrow">arrow_back</text>
        <text class="check-btn-text">返回</text>
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
const stopSpeaking = ref(false) // Flag to stop ongoing speakMultiple

const words = computed(() => items.value.map(i => i.content))

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

async function loadItems() {
  try {
    items.value = await getDictationItems(taskId.value)
    if (taskId.value) {
      await tasksStore.updateStatus(taskId.value, 'in_progress')
      // Get task title from tasksStore
      const task = tasksStore.tasks.find(t => t.id === taskId.value)
      if (task) {
        taskTitle.value = task.title
      }
    }
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

function speak(text: string): Promise<void> {
  return new Promise((resolve) => {
    // Check if we should stop before even starting
    if (stopSpeaking.value) {
      resolve()
      return
    }

    // #ifdef APP-PLUS
    ;(plus.speech as any).startSpeak(text, {
      rate: 1.0,
      onComplete: () => resolve(),
      onError: () => resolve(),
    })
    // #endif

    // #ifdef H5
    const utter = new SpeechSynthesisUtterance(text)
    utter.rate = 1.0
    utter.lang = 'zh-CN'

    let resolved = false
    let checkInterval: ReturnType<typeof setInterval> | null = null

    const doResolve = () => {
      if (!resolved) {
        resolved = true
        if (checkInterval) clearInterval(checkInterval)
        resolve()
      }
    }

    utter.onend = doResolve
    utter.onerror = doResolve
    speechSynthesis.speak(utter)

    // Poll to check if we should stop (needed because cancel might not trigger onend immediately)
    checkInterval = setInterval(() => {
      if (stopSpeaking.value) {
        speechSynthesis.cancel()
        doResolve()
      }
    }, 50)
    // #endif
  })
}

// Speak a word multiple times with pauses between
async function speakMultiple(text: string, times: number = 3, pauseMs: number = 800): Promise<void> {
  for (let i = 0; i < times; i++) {
    if (stopSpeaking.value) return // Check if we should stop
    await speak(text)
    if (stopSpeaking.value) return // Check after speak
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

  resumeSpeech() // Reset stop flag
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

// User taps a word to play - this pauses auto-play
async function playSingleWord(index: number) {
  if (currentIndex.value === index) return

  // Stop any current speech and auto-play timer
  stopSpeech()
  clearAutoPlayTimer()

  // Wait for stop to take effect (speak() polls every 50ms, so 150ms should be enough)
  await delay(150)

  // Pause auto-play mode - user needs to click "继续" to resume
  isPlaying.value = false

  if (!ttsReady.value) {
    await initTTS()
  }

  // Reset stop flag and play the clicked word
  resumeSpeech()
  currentIndex.value = index
  await speakMultiple(words.value[index], 3)
  playedWords[index] = true
  currentIndex.value = -1
  // Do NOT auto-continue - user is now in manual mode
}

async function startDictation() {
  if (allPlayed.value) return

  if (!ttsReady.value) {
    uni.showToast({ title: '正在初始化语音...', icon: 'none' })
    await initTTS()
  }

  await warmUpTTS()

  isPlaying.value = true
  // Always start from first unplayed word
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

  // Reset state for new task
  Object.keys(playedWords).forEach(key => delete playedWords[key])
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
  stopSpeaking.value = true // Signal speakMultiple to stop

  // #ifdef H5
  speechSynthesis.cancel()
  // #endif

  // #ifdef APP-PLUS
  try { (plus.speech as any).stopSpeak() } catch {}
  // #endif
}

function resumeSpeech() {
  stopSpeaking.value = false // Reset flag when starting new speech
}

onLoad(async (query) => {
  // Check for continuous mode
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
  margin-top: 20px;
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
  margin-bottom: $spacing-md; box-shadow: 0 2px 4px rgba(0,0,0,0.04);
}
.intro-star { font-size: 20px; }
.intro-text { font-size: $font-body-md; color: $color-on-surface-variant; }

// Task info
.task-info {
  padding: $spacing-xs $spacing-md;
  background: $color-primary-fixed;
  border-radius: $radius-full;
  margin-bottom: $spacing-md;
}
.task-info-text {
  font-family: $font-family; font-size: $font-label-md; font-weight: 600;
  color: $color-primary;
}

// Word list section
.word-list-section {
  width: 100%; max-width: 320px;
}
.section-title {
  font-family: $font-family; font-size: $font-headline-lg; font-weight: 600;
  color: $color-on-surface; text-align: center; display: block; margin-bottom: $spacing-xs;
}
.task-title-display {
  font-family: $font-family; font-size: $font-body-md; font-weight: 500;
  color: $color-on-surface-variant; text-align: center; display: block; margin-bottom: $spacing-md;
}
.word-list {
  display: flex; flex-direction: column; gap: $spacing-sm;
}
.word-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: $spacing-md; background: $color-surface-container;
  border-radius: $radius-xl; border: 2px solid transparent;
  transition: all 0.2s;
  &:active {
    background: $color-surface-container-high;
    transform: scale(0.98);
  }
}
.word-item-played {
  border-color: $color-tertiary;
}
.word-item-playing {
  border-color: $color-primary;
  background: $color-primary-fixed;
}
.word-left {
  display: flex; align-items: center; gap: $spacing-md;
}
.play-btn {
  width: 44px; height: 44px; border-radius: $radius-full;
  background: $color-surface-container-high; display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.play-btn-done {
  background: $color-tertiary;
}
.play-btn-active {
  background: $color-primary;
  box-shadow: 0 0 0 4px rgba(0, 88, 189, 0.2);
}
.play-icon { font-size: 26px; color: $color-on-surface-variant; }
.play-btn-done .play-icon { color: $color-on-tertiary; }
.play-btn-active .play-icon { color: $color-on-primary; }
.word-number {
  font-family: $font-family; font-size: $font-body-lg; font-weight: 500;
  color: $color-on-surface;
}
.word-text {
  font-family: $font-family; font-size: $font-body-lg; font-weight: 500;
  color: $color-on-surface;
}
.tap-hint {
  padding: 4px 12px; background: $color-primary-fixed; border-radius: $radius-full;
}
.tap-hint-text {
  font-family: $font-family; font-size: $font-label-sm; font-weight: 600;
  color: $color-primary;
}
.status-icon {
  font-size: 24px; color: $color-tertiary;
}

// Bottom action
.bottom-action {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 20;
  padding-left: $spacing-margin; padding-right: $spacing-margin; padding-top: $spacing-xl;
  background: linear-gradient(to top, $color-surface 60%, transparent);
}
.action-btn-row {
  display: flex; justify-content: center;
}
.action-btn {
  display: flex; align-items: center; justify-content: center; gap: $spacing-sm;
  min-width: 200px; padding: 18px $spacing-xl; border-radius: $radius-xl;
  font-family: $font-family; font-size: $font-headline-lg; font-weight: 600;
  border-bottom: 6px solid transparent;
  &:active { border-bottom-width: 0; transform: translateY(6px); }
}
.btn-start {
  background: $color-tertiary-container; color: $color-on-tertiary-container;
  border-bottom-color: $color-on-tertiary-fixed-variant;
}
.btn-playing {
  background: $color-primary; color: $color-on-primary;
  border-bottom-color: $color-on-primary-fixed-variant;
}
.btn-icon { font-size: 28px; }
.action-btn-text { color: inherit; }
.check-btn {
  display: flex; align-items: center; justify-content: center; gap: $spacing-md;
  background: $color-tertiary-container; color: $color-on-tertiary-container;
  padding: 18px; border-radius: $radius-xl;
  border-bottom: 6px solid $color-on-tertiary-fixed-variant;
  font-family: $font-family; font-size: $font-headline-lg; font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 131, 121, 0.2);
  &:active { border-bottom-width: 0; transform: translateY(6px); }
}
.check-btn-back {
  background: $color-primary; color: $color-on-primary;
  border-bottom-color: $color-on-primary-fixed-variant;
  box-shadow: 0 4px 12px rgba(0, 88, 189, 0.2);
}
.check-btn-text { color: inherit; }
.check-arrow { font-size: 28px; font-variation-settings: 'wght' 600; color: inherit; }
</style>
