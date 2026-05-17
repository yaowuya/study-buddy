<template>
  <view class="page">
    <!-- AppBar -->
    <view class="appbar" :style="{ paddingTop: Math.max(statusBarHeight, 12) + 'px' }">
      <view class="appbar-left">
        <view class="avatar-circle">
          <text class="material-symbols-outlined">person</text>
        </view>
        <text class="appbar-title">作业伙伴</text>
      </view>
    </view>

    <!-- Main -->
    <scroll-view scroll-y class="main" :style="{ paddingTop: (appbarHeight + 8) + 'px' }">
      <!-- Hero Overview Card -->
      <view class="hero-card">
        <view class="hero-deco"></view>
        <view class="hero-top">
          <text class="material-symbols-outlined hero-icon">sentiment_satisfied</text>
          <text class="hero-title">今日作业概览</text>
        </view>
        <text class="hero-body">
          今天共有 <text class="hero-num">{{ tasks.length }}</text> 项作业，已完成
          <text class="hero-num-done">{{ doneCount }}</text> 项。
        </text>
        <view class="progress-row">
          <text class="progress-label">整体进度</text>
          <text class="progress-pct">{{ progressPct }}%</text>
        </view>
        <view class="progress-bar-bg">
          <view class="progress-bar-fill" :style="{ width: progressPct + '%' }"></view>
        </view>
      </view>

      <!-- Pending Tasks -->
      <view class="section">
        <text class="section-label">待完成 ({{ pendingTasks.length }})</text>
        <view v-for="task in pendingTasks" :key="task.id" class="task-card">
          <view class="task-card-top">
            <view :class="['task-icon-box', `icon-${task.subject || 'default'}`]">
              <text class="material-symbols-outlined">{{ subjectIcon(task.subject) }}</text>
            </view>
            <view class="task-card-info">
              <view class="title-row">
                <text class="task-card-title">{{ task.title }}</text>
                <view v-if="task.has_dictation" class="dictation-tag" @tap="previewDictation(task)">
                  <text class="material-symbols-outlined tag-icon">record_voice_over</text>
                  <text class="tag-text">听写</text>
                </view>
              </view>
              <view v-if="task.duration" class="task-meta">
                <text class="material-symbols-outlined meta-icon">timer</text>
                <text class="task-meta-text">预计 {{ task.duration }} 分钟</text>
              </view>
            </view>
          </view>
          <text v-if="task.desc" class="task-desc">{{ task.desc }}</text>
          <view class="btn-row">
            <view v-if="task.has_dictation" class="preview-btn" @tap="previewDictation(task)">
              <text class="material-symbols-outlined btn-icon">volume_up</text>
              <text class="btn-text">预览听写</text>
            </view>
            <view class="edit-btn" @tap="editTask(task)">
              <text class="material-symbols-outlined btn-icon">edit</text>
              <text class="btn-text">编辑</text>
            </view>
          </view>
        </view>
        <view v-if="pendingTasks.length === 0" class="empty-hint">
          <text class="empty-hint-text">暂无待完成任务</text>
        </view>
      </view>

      <!-- Completed Tasks -->
      <view v-if="doneTasks.length > 0" class="section">
        <text class="section-label section-label-done">已完成 ({{ doneTasks.length }})</text>
        <view v-for="task in doneTasks" :key="task.id" class="task-card task-card-done">
          <view class="task-card-top">
            <view :class="['task-icon-box', `icon-${task.subject || 'default'}`, 'icon-done']">
              <text class="material-symbols-outlined">{{ subjectIcon(task.subject) }}</text>
            </view>
            <view class="task-card-info">
              <view class="title-row">
                <text class="task-card-title task-title-done">{{ task.title }}</text>
                <view v-if="task.has_dictation" class="dictation-tag dictation-tag-done" @tap="previewDictation(task)">
                  <text class="material-symbols-outlined tag-icon">record_voice_over</text>
                  <text class="tag-text">听写</text>
                </view>
              </view>
              <text v-if="task.desc" class="task-meta-text">{{ task.desc }}</text>
            </view>
            <view class="check-circle">
              <text class="material-symbols-outlined check-icon">check</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Family Code Modal -->
      <view v-if="showCode" class="modal-overlay" @tap="showCode = false">
        <view class="modal-content" @tap.stop>
          <text class="modal-title">家庭连接码</text>
          <text class="modal-code">{{ familyCode }}</text>
          <text class="modal-hint">让学生输入此码完成绑定</text>
        </view>
      </view>

      <!-- Dictation Preview Modal -->
      <view v-if="dictationModal.visible" class="modal-overlay" @tap="closeDictationModal">
        <view class="dictation-modal" @tap.stop>
          <view class="dictation-modal-header">
            <text class="dictation-modal-title">听写预览</text>
            <view class="close-btn" @tap="closeDictationModal">
              <text class="material-symbols-outlined">close</text>
            </view>
          </view>
          <text class="dictation-modal-subtitle">{{ dictationModal.taskTitle }}</text>

          <view v-if="dictationModal.loading" class="dictation-loading">
            <text>加载中...</text>
          </view>
          <view v-else class="dictation-words">
            <view
              v-for="(word, i) in dictationModal.words"
              :key="i"
              :class="['word-chip', playingIndex === i ? 'word-chip-playing' : '']"
              @tap="playWord(word, i)"
            >
              <text class="word-text">{{ word }}</text>
              <text class="material-symbols-outlined word-play-icon">
                {{ playingIndex === i ? 'volume_up' : 'play_arrow' }}
              </text>
            </view>
          </view>

          <view class="dictation-modal-actions">
            <view class="play-all-btn" @tap="playAllWords">
              <text class="material-symbols-outlined">playlist_play</text>
              <text>顺序播放</text>
            </view>
          </view>
        </view>
      </view>

      <view class="bottom-spacer"></view>
    </scroll-view>

    <!-- Bottom Nav -->
    <view class="bottom-nav" :style="{ paddingBottom: safeAreaBottom + 'px' }">
      <view class="nav-item nav-item-active">
        <text class="material-symbols-outlined nav-icon">auto_stories</text>
        <text class="nav-label">作业</text>
      </view>
      <view class="nav-item" @tap="goCreate">
        <text class="material-symbols-outlined nav-icon">add_circle</text>
        <text class="nav-label">布置</text>
      </view>
      <view class="nav-item" @tap="goGrading">
        <text class="material-symbols-outlined nav-icon">history</text>
        <text class="nav-label">历史</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { useTasksStore } from '@/stores/tasks'
import { useSyncStore } from '@/stores/sync'
import { getDictationItems } from '@/api/dictation'
import type { TaskOut } from '@/api/tasks'
import { BASE_URL } from '@/api/config'

const authStore = useAuthStore()
const tasksStore = useTasksStore()
const syncStore = useSyncStore()
const showCode = ref(false)
const familyCode = ref('加载中')

const statusBarHeight = ref(0)
const safeAreaBottom = ref(0)
const appbarHeight = ref(88) // 增加默认值，确保不被遮住

// Dictation preview
const dictationModal = reactive({
  visible: false,
  loading: false,
  taskId: '',
  taskTitle: '',
  words: [] as string[],
})
const playingIndex = ref(-1)

async function loadFamilyCode() {
  if (!authStore.user?.family_id) {
    familyCode.value = '未绑定'
    return
  }
  try {
    const { request } = await import('@/api/request')
    const family = await request<{ code: string }>('/auth/family', 'GET')
    familyCode.value = family.code
  } catch {
    familyCode.value = '获取失败'
  }
}

const tasks = computed(() => Array.isArray(tasksStore.tasks) ? tasksStore.tasks : [])
const pendingTasks = computed(() => tasks.value.filter(t => t.status === 'pending' || t.status === 'in_progress'))
const doneTasks = computed(() => tasks.value.filter(t => t.status === 'submitted' || t.status === 'graded'))
const doneCount = computed(() => doneTasks.value.length)
const progressPct = computed(() => {
  if (tasks.value.length === 0) return 0
  return Math.round((doneCount.value / tasks.value.length) * 100)
})

function subjectIcon(subject: string | null) {
  const map: Record<string, string> = { '语文': 'edit_note', '数学': 'calculate', '英语': 'translate', '科学': 'science' }
  return map[subject || ''] || 'assignment'
}

function editTask(task: TaskOut) {
  uni.navigateTo({ url: `/pages/parent/task-edit?id=${task.id}` })
}

async function previewDictation(task: TaskOut) {
  dictationModal.visible = true
  dictationModal.loading = true
  dictationModal.taskId = task.id
  dictationModal.taskTitle = task.title
  dictationModal.words = []
  playingIndex.value = -1

  try {
    const items = await getDictationItems(task.id)
    dictationModal.words = items.map(i => i.content)
  } catch (e: any) {
    uni.showToast({ title: e.message || '加载失败', icon: 'none' })
  } finally {
    dictationModal.loading = false
  }
}

function closeDictationModal() {
  dictationModal.visible = false
  stopSpeech()
}

let dashboardAudioContext: UniApp.InnerAudioContext | null = null

function getTTSAudioUrl(text: string, rate: number = 1.0): string {
  return `${BASE_URL}/tts/speak?text=${encodeURIComponent(text)}&rate=${rate}`
}

function speak(text: string): Promise<void> {
  return new Promise((resolve) => {
    console.log('[TTS] 开始播放:', text)

    try {
      if (dashboardAudioContext) {
        dashboardAudioContext.destroy()
      }

      const url = getTTSAudioUrl(text)
      console.log('[TTS] 请求 URL:', url)

      dashboardAudioContext = uni.createInnerAudioContext()
      dashboardAudioContext.volume = 1.0
      dashboardAudioContext.src = url

      dashboardAudioContext.onCanplay(() => {
        console.log('[TTS] 音频可播放')
        dashboardAudioContext?.play()
      })

      dashboardAudioContext.onPlay(() => {
        console.log('[TTS] 正在播放')
      })

      dashboardAudioContext.onEnded(() => {
        console.log('[TTS] 播放完成')
        dashboardAudioContext?.destroy()
        dashboardAudioContext = null
        resolve()
      })

      dashboardAudioContext.onError((e) => {
        console.error('[TTS] 播放失败:', e)
        console.error('[TTS] 失败 URL:', url)
        dashboardAudioContext?.destroy()
        dashboardAudioContext = null
        resolve()
      })
    } catch (e) {
      console.error('[TTS] 异常:', e)
      resolve()
    }
  })
}

function stopSpeech() {
  playingIndex.value = -1
  try {
    if (dashboardAudioContext) {
      dashboardAudioContext.stop()
      dashboardAudioContext.destroy()
      dashboardAudioContext = null
    }
  } catch {}
}

async function playWord(word: string, index: number) {
  stopSpeech()
  playingIndex.value = index
  await speak(word)
  playingIndex.value = -1
}

async function playAllWords() {
  stopSpeech()
  for (let i = 0; i < dictationModal.words.length; i++) {
    playingIndex.value = i
    await speak(dictationModal.words[i])
    await new Promise(r => setTimeout(r, 1500))
  }
  playingIndex.value = -1
}

function goCreate() {
  uni.redirectTo({ url: '/pages/parent/task-create' })
}

function goGrading() {
  uni.redirectTo({ url: '/pages/parent/grading' })
}

onMounted(() => {
  const info = uni.getSystemInfoSync()
  statusBarHeight.value = info.statusBarHeight || 0
  safeAreaBottom.value = info.safeAreaInsets?.bottom || 0
  // AppBar 高度 = statusBarHeight + 顶部padding + 内容高度(56) + 底部padding
  appbarHeight.value = Math.max(statusBarHeight.value, 12) + 56 + 12
  tasksStore.loadCached()
  loadFamilyCode()
})

onShow(() => {
  tasksStore.fetchTodayTasks()
  syncStore.start()
})

onUnmounted(() => {
  stopSpeech()
})
</script>

<style lang="scss" scoped>
@use '@/static/styles/variables.scss' as *;

.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-weight: normal;
  font-style: normal;
  font-size: 24px;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-feature-settings: 'liga';
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.page { min-height: 100vh; background: $color-surface; font-family: $font-family-body; }

// AppBar
.appbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: #fff; border-bottom: 2px solid #f1f5f9;
  display: flex; align-items: center; justify-content: space-between;
  padding-left: $spacing-margin; padding-right: $spacing-margin;
  padding-bottom: 12px;
  padding-top: 12px;
  min-height: 64px; box-sizing: border-box;
}
.appbar-left { display: flex; align-items: center; gap: $spacing-sm; }
.avatar-circle {
  width: 40px; height: 40px; border-radius: $radius-full;
  background: $color-surface-container; display: flex; align-items: center; justify-content: center;
  color: $color-primary;
}
.appbar-title { font-family: $font-family; font-size: 18px; font-weight: 700; color: #2563eb; }

// Main scroll area
.main { flex: 1; padding-left: $spacing-margin; padding-right: $spacing-margin; box-sizing: border-box; width: 100%; }

// Hero card
.hero-card {
  background: $color-primary-container; border-radius: $radius-2xl;
  padding: $spacing-md; margin-bottom: $spacing-lg;
  position: relative; overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 88, 189, 0.15);
}
.hero-deco {
  position: absolute; right: 0; top: 0; width: 128px; height: 128px;
  background: linear-gradient(to bottom-left, rgba(255,255,255,0.2), transparent);
  border-bottom-left-radius: $radius-full; pointer-events: none;
}
.hero-top { display: flex; align-items: center; gap: $spacing-sm; margin-bottom: $spacing-xs; }
.hero-icon { color: $color-on-primary-fixed-variant; font-size: 28px; }
.hero-title { font-family: $font-family; font-size: $font-headline-lg; font-weight: 600; color: #fefcff; }
.hero-body { font-size: $font-body-md; color: rgba(254,252,255,0.9); display: block; margin-bottom: $spacing-sm; }
.hero-num { font-weight: 700; }
.hero-num-done { font-weight: 700; color: $color-tertiary-fixed; }
.progress-row { display: flex; justify-content: space-between; margin-bottom: 4px; }
.progress-label { font-size: $font-label-sm; color: rgba(254,252,255,0.8); }
.progress-pct { font-size: $font-label-sm; color: #fefcff; font-weight: 600; }
.progress-bar-bg {
  width: 100%; height: 16px; background: $color-on-primary-fixed-variant;
  border-radius: $radius-full; overflow: hidden;
}
.progress-bar-fill { height: 100%; background: $color-tertiary-fixed; border-radius: $radius-full; transition: width 0.3s; }

// Sections
.section { margin-bottom: $spacing-lg; }
.section-label {
  font-family: $font-family; font-size: $font-label-md; font-weight: 600;
  color: $color-on-surface-variant; letter-spacing: 0.05em; display: block; margin-bottom: $spacing-md;
}
.section-label-done { opacity: 0.8; }

// Task cards
.task-card {
  background: $color-surface-container-lowest; border-radius: $radius-xl;
  padding: $card-padding; border: 2px solid $color-surface-container-highest;
  box-shadow: 0 4px 12px rgba(0, 88, 189, 0.04); margin-bottom: $spacing-md;
  display: flex; flex-direction: column; gap: $spacing-sm;
}
.task-card-done {
  background: rgba(0, 131, 121, 0.06); border-color: rgba(0, 104, 95, 0.2);
}
.task-card-top { display: flex; align-items: center; gap: $spacing-sm; }
.task-icon-box {
  width: 48px; height: 48px; border-radius: $radius-xl; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: $color-primary-fixed; color: $color-primary;
}
.icon-语文 { background: $color-surface-container; color: $color-tertiary; }
.icon-数学 { background: $color-primary-fixed; color: $color-primary; }
.icon-英语 { background: $color-secondary-fixed; color: $color-secondary; }
.icon-科学 { background: $color-tertiary-fixed; color: $color-on-tertiary-fixed-variant; }
.icon-default { background: $color-surface-container; color: $color-on-surface-variant; }
.icon-done { opacity: 0.7; }
.task-card-info { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.title-row { display: flex; align-items: center; gap: $spacing-xs; flex-wrap: wrap; line-height: 1; }
.task-card-title {
  font-family: $font-family; font-size: 18px; font-weight: 700;
  color: $color-on-surface; line-height: 24px;
}
.dictation-tag {
  display: inline-flex; align-items: center; gap: 2px;
  background: $color-tertiary-container; padding: 2px 8px; border-radius: $radius-full;
  height: 24px; box-sizing: border-box;
}
.tag-icon { font-size: 14px; color: $color-on-tertiary-container; line-height: 1; }
.tag-text { font-size: 12px; font-weight: 600; color: $color-on-tertiary-container; line-height: 1; }
.dictation-tag-done { background: rgba(0, 131, 121, 0.15); }
.task-title-done { color: $color-tertiary; }
.task-meta { display: flex; align-items: center; gap: 4px; margin-top: 4px; }
.meta-icon { font-size: 14px; color: $color-on-surface-variant; }
.task-meta-text { font-size: $font-label-sm; color: $color-on-surface-variant; }
.task-desc {
  font-size: $font-body-md; color: $color-on-surface-variant;
  background: $color-surface-bright; padding: $spacing-sm;
  border-radius: $radius-lg; border: 1px solid rgba($color-outline-variant, 0.3);
}
.check-circle {
  width: 32px; height: 32px; border-radius: $radius-full;
  background: $color-tertiary; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.check-icon { color: $color-on-tertiary; font-size: 20px; }

// Button row
.btn-row { display: flex; gap: $spacing-sm; }
.preview-btn, .edit-btn {
  flex: 1;
  display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: $spacing-sm; border-radius: $radius-xl;
  font-family: $font-family; font-size: $font-label-md; font-weight: 600;
  border-bottom: 3px solid transparent;
  &:active { border-bottom-width: 0; transform: translateY(3px); }
}
.preview-btn {
  background: $color-tertiary-container; color: $color-on-tertiary-container;
  border-bottom-color: $color-on-tertiary-fixed-variant;
}
.edit-btn {
  background: $color-primary; color: $color-on-primary;
  border-bottom-color: $color-on-primary-fixed-variant;
}
.btn-icon { font-size: 16px; }
.btn-text { color: inherit; }

.empty-hint { padding: $spacing-md; text-align: center; }
.empty-hint-text { color: $color-on-surface-variant; font-size: $font-body-md; }
.bottom-spacer { height: 100px; }

// Modal
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 999;
}
.modal-content {
  background: #fff; padding: $spacing-lg; border-radius: $radius-2xl; text-align: center; width: 300px;
}
.modal-title { font-size: $font-card-title; font-weight: 600; display: block; margin-bottom: $spacing-md; }
.modal-code { font-size: 40px; font-weight: 700; color: $color-primary; letter-spacing: 8px; display: block; margin-bottom: $spacing-sm; }
.modal-hint { font-size: $font-body-md; color: $color-on-surface-variant; display: block; }

// Dictation Preview Modal
.dictation-modal {
  background: #fff; border-radius: $radius-2xl; width: 340px; max-width: 90vw;
  max-height: 80vh; display: flex; flex-direction: column; overflow: hidden;
}
.dictation-modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: $spacing-md; border-bottom: 1px solid $color-surface-container-high;
}
.dictation-modal-title {
  font-family: $font-family; font-size: $font-headline-lg; font-weight: 600;
  color: $color-on-surface;
}
.close-btn {
  width: 36px; height: 36px; border-radius: $radius-full;
  background: $color-surface-container; display: flex; align-items: center; justify-content: center;
  color: $color-on-surface-variant;
}
.dictation-modal-subtitle {
  font-size: $font-body-md; color: $color-on-surface-variant;
  padding: 0 $spacing-md $spacing-sm;
}
.dictation-loading {
  padding: $spacing-xl; text-align: center; color: $color-on-surface-variant;
}
.dictation-words {
  display: flex; flex-wrap: wrap; gap: $spacing-sm;
  padding: $spacing-md; overflow-y: auto;
}
.word-chip {
  display: flex; align-items: center; gap: $spacing-xs;
  background: $color-surface-container; padding: $spacing-sm $spacing-md;
  border-radius: $radius-xl; border: 2px solid transparent;
  transition: all 0.2s;
}
.word-chip-playing {
  background: $color-tertiary-container; border-color: $color-tertiary;
}
.word-text { font-family: $font-family; font-size: $font-body-lg; font-weight: 600; color: $color-on-surface; }
.word-play-icon { font-size: 20px; color: $color-on-surface-variant; }
.word-chip-playing .word-play-icon { color: $color-tertiary; }
.dictation-modal-actions {
  padding: $spacing-md; border-top: 1px solid $color-surface-container-high;
}
.play-all-btn {
  display: flex; align-items: center; justify-content: center; gap: $spacing-sm;
  background: $color-primary; color: $color-on-primary;
  padding: $spacing-sm $spacing-md; border-radius: $radius-xl;
  font-family: $font-family; font-size: $font-label-md; font-weight: 600;
  border-bottom: 3px solid $color-on-primary-fixed-variant;
  &:active { border-bottom-width: 0; transform: translateY(3px); }
}

// Bottom Nav
.bottom-nav {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 100;
  background: #fff; border-top: 2px solid #f1f5f9;
  display: flex; justify-content: space-around; align-items: center;
  height: 80px; padding-left: $spacing-md; padding-right: $spacing-md;
  box-shadow: 0 -4px 10px rgba(58, 134, 255, 0.05);
}
.nav-item {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 6px 20px; color: #94a3b8;
}
.nav-item-active {
  background: #dbeafe; color: #1d4ed8; border-radius: $radius-2xl;
}
.nav-icon { font-size: 24px; }
.nav-label { font-family: $font-family; font-size: 12px; font-weight: 500; margin-top: 4px; }
</style>
