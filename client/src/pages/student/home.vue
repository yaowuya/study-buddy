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
      <view class="appbar-icon-btn">
        <text class="material-symbols-outlined">notifications</text>
      </view>
    </view>

    <scroll-view scroll-y class="main" :style="{ paddingTop: (Math.max(statusBarHeight, 12) + 56) + 'px' }">
      <!-- Hero: Greeting + Progress -->
      <view class="hero-section">
        <view class="hero-text">
          <text class="hero-greeting">你好！</text>
          <text class="hero-sub">今天也要加油鸭～</text>
        </view>
        <view class="progress-circle-wrap">
          <!-- SVG circular progress (H5 only) -->
          <svg class="progress-svg" viewBox="0 0 100 100" width="96" height="96">
            <circle class="progress-bg" cx="50" cy="50" r="40" fill="none" stroke-width="12"></circle>
            <circle class="progress-fg" cx="50" cy="50" r="40" fill="none" stroke-width="12"
              stroke-dasharray="251.2"
              :stroke-dashoffset="251.2 - (251.2 * progressRatio)"
              stroke-linecap="round"
              transform="rotate(-90 50 50)"></circle>
          </svg>
          <view class="progress-center">
            <text class="progress-fraction">{{ doneCount }}/{{ tasks.length }}</text>
            <text class="progress-done-label">已完成</text>
          </view>
        </view>
      </view>

      <!-- Dictation CTA -->
      <view class="dictation-cta" @tap="goDictation">
        <view class="cta-deco"></view>
        <view class="cta-left">
          <view class="cta-icon-box">
            <text class="material-symbols-outlined cta-icon">mic</text>
          </view>
          <view class="cta-text">
            <text class="cta-title">听写作业</text>
            <text class="cta-sub">进入今天的听写练习</text>
          </view>
        </view>
        <text class="material-symbols-outlined cta-arrow">arrow_forward_ios</text>
      </view>

      <!-- Task List -->
      <view class="task-section">
        <text class="section-title">今日作业</text>
        <view v-if="tasks.length === 0" class="empty-state">
          <text class="empty-text">今天没有任务，休息一下吧！</text>
        </view>
        <view v-for="task in tasks" :key="task.id" :class="['task-card', task.status === 'graded' ? 'task-done' : 'task-pending']" @tap="handleTaskTap(task)">
          <view class="task-card-inner">
            <view :class="['task-icon-box', `icon-${task.subject || 'default'}`]">
              <text class="material-symbols-outlined">{{ subjectIcon(task.subject) }}</text>
            </view>
            <view class="task-info">
              <view class="task-title-row">
                <text :class="['task-title', task.status === 'graded' ? 'task-title-done' : '']">{{ task.title }}</text>
                <view v-if="task.status === 'graded'" class="check-circle">
                  <text class="material-symbols-outlined check-icon">check</text>
                </view>
                <view v-else class="empty-circle"></view>
              </view>
              <text v-if="task.desc" :class="['task-desc', task.status === 'graded' ? 'task-desc-done' : '']">{{ task.desc }}</text>
            </view>
          </view>
          <!-- Action row -->
          <view class="task-action">
            <view v-if="task.status === 'pending'" class="action-btn btn-start" @tap.stop="startTask(task)">
              <text class="action-btn-text">开始</text>
            </view>
            <view v-if="task.status === 'in_progress'" class="action-btn btn-done" @tap.stop="doneTask(task)">
              <text class="action-btn-text">完成</text>
            </view>
            <text v-if="task.status === 'submitted'" class="action-wait">等待批改</text>
          </view>
        </view>
      </view>

      <!-- Celebration overlay -->
      <view v-if="showCelebration" class="celebration" @tap="showCelebration = false">
        <text class="celebration-emoji">🎉</text>
        <text class="celebration-text">太棒了！全部完成！</text>
      </view>

      <view class="bottom-spacer"></view>
    </scroll-view>

    <!-- Bottom Nav -->
    <view class="bottom-nav" :style="{ paddingBottom: safeAreaBottom + 'px' }">
      <view class="nav-item nav-item-active">
        <text class="material-symbols-outlined nav-icon">assignment</text>
        <text class="nav-label">作业</text>
      </view>
      <view class="nav-item" @tap="goHistory">
        <text class="material-symbols-outlined nav-icon">history</text>
        <text class="nav-label">历史</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useTasksStore } from '@/stores/tasks'
import { useSyncStore } from '@/stores/sync'
import type { TaskOut } from '@/api/tasks'

const tasksStore = useTasksStore()
const syncStore = useSyncStore()
const statusBarHeight = ref(0)
const safeAreaBottom = ref(0)
const showCelebration = ref(false)

const tasks = computed(() => tasksStore.tasks)
const doneCount = computed(() => tasks.value.filter(t => t.status === 'graded').length)
const progressRatio = computed(() => tasks.value.length === 0 ? 0 : doneCount.value / tasks.value.length)

function subjectIcon(subject: string | null) {
  const map: Record<string, string> = { '语文': 'edit_note', '数学': 'calculate', '英语': 'translate', '科学': 'science' }
  return map[subject || ''] || 'assignment'
}

function handleTaskTap(task: TaskOut) {
  if (task.type === 'school' && task.status !== 'graded') {
    uni.navigateTo({ url: `/pages/student/dictation?taskId=${task.id}` })
  }
}

async function startTask(task: TaskOut) {
  await tasksStore.updateStatus(task.id, 'in_progress')
}

async function doneTask(task: TaskOut) {
  await tasksStore.submitTask(task.id)
  if (tasksStore.allCompleted()) {
    showCelebration.value = true
  }
}

function goDictation() {
  const dictationTask = tasks.value.find(t => t.status !== 'graded')
  if (dictationTask) {
    uni.navigateTo({ url: `/pages/student/dictation?taskId=${dictationTask.id}` })
  } else {
    uni.showToast({ title: '没有待完成的听写任务', icon: 'none' })
  }
}

function goHistory() {
  uni.showToast({ title: '历史记录（开发中）', icon: 'none' })
}

onMounted(() => {
  const info = uni.getSystemInfoSync()
  statusBarHeight.value = info.statusBarHeight || 0
  safeAreaBottom.value = info.safeAreaInsets?.bottom || 0
  tasksStore.loadCached()
})

onShow(() => {
  tasksStore.fetchTodayTasks()
  syncStore.start()
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

.page { min-height: 100vh; background: $color-surface; font-family: $font-family-body; }

.appbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: rgba(255,255,255,0.9); border-bottom: 2px solid #f1f5f9;
  backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: space-between;
  padding-left: $spacing-margin; padding-right: $spacing-margin; padding-bottom: 12px;
}
.appbar-left { display: flex; align-items: center; gap: 12px; }
.avatar-circle {
  width: 40px; height: 40px; border-radius: $radius-full;
  background: $color-primary-fixed; display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}
.appbar-title { font-family: $font-family; font-size: 18px; font-weight: 700; color: #3b82f6; }
.appbar-icon-btn {
  width: 40px; height: 40px; border-radius: $radius-full;
  display: flex; align-items: center; justify-content: center; color: #94a3b8;
}

.main { flex: 1; padding: 0 $spacing-margin; box-sizing: border-box; width: 100%; }

// Hero
.hero-section {
  background: $color-surface-container; border-radius: 24px; padding: 24px;
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: $spacing-md; border: 1px solid $color-surface-variant;
  position: relative; overflow: hidden;
}
.hero-text { z-index: 1; }
.hero-greeting { font-family: $font-family; font-size: 32px; font-weight: 700; color: $color-on-surface; display: block; margin-bottom: 8px; }
.hero-sub { font-size: $font-body-md; color: $color-on-surface-variant; display: block; }
.progress-circle-wrap { position: relative; width: 96px; height: 96px; flex-shrink: 0; z-index: 1; }
.progress-svg { position: absolute; top: 0; left: 0; }
.progress-bg { stroke: $color-surface-variant; }
.progress-fg { stroke: $color-tertiary; }
.progress-center {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.progress-fraction { font-family: $font-family; font-size: $font-headline-lg; font-weight: 600; color: $color-tertiary; }
.progress-done-label { font-family: $font-family; font-size: $font-label-sm; color: $color-on-surface-variant; }

// Dictation CTA
.dictation-cta {
  background: $color-primary-container; color: $color-on-primary-container;
  border-radius: 20px; padding: 24px;
  border-bottom: 4px solid $color-primary;
  box-shadow: 0 8px 16px rgba(20, 112, 232, 0.2);
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: $spacing-lg; position: relative; overflow: hidden;
  &:active { border-bottom-width: 0; transform: translateY(4px); }
}
.cta-deco {
  position: absolute; right: 0; top: 0; width: 128px; height: 128px;
  background: rgba(255,255,255,0.1); border-radius: $radius-full; margin-right: -40px; margin-top: -40px;
  pointer-events: none;
}
.cta-left { display: flex; align-items: center; gap: 16px; position: relative; z-index: 1; }
.cta-icon-box {
  width: 56px; height: 56px; background: rgba(255,255,255,0.2); border-radius: $radius-2xl;
  display: flex; align-items: center; justify-content: center;
}
.cta-icon { font-size: 36px; color: $color-on-primary-container; }
.cta-text { display: flex; flex-direction: column; }
.cta-title { font-family: $font-family; font-size: $font-headline-lg; font-weight: 600; color: $color-on-primary-container; }
.cta-sub { font-size: $font-body-md; color: rgba(254,252,255,0.9); margin-top: 4px; }
.cta-arrow { font-size: 28px; color: $color-on-primary-container; position: relative; z-index: 1; }

// Task section
.task-section { display: flex; flex-direction: column; gap: $spacing-sm; }
.section-title { font-family: $font-family; font-size: $font-headline-lg; font-weight: 600; color: $color-on-surface; display: block; margin-bottom: 8px; }

.task-card {
  background: $color-surface; border-radius: $radius-2xl; padding: 20px;
  border: 2px solid $color-outline-variant;
  box-shadow: 0 4px 12px rgba(17, 28, 42, 0.03);
  display: flex; flex-direction: column; gap: $spacing-sm;
}
.task-done {
  border-color: $color-tertiary;
  box-shadow: 0 4px 12px rgba(0, 104, 95, 0.05);
}
.task-card-inner { display: flex; align-items: flex-start; gap: 16px; }
.task-icon-box {
  width: 48px; height: 48px; border-radius: $radius-xl; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: $color-primary-fixed; color: $color-primary;
}
.icon-语文 { background: rgba(0, 131, 121, 0.15); color: $color-tertiary; }
.icon-数学 { background: $color-primary-fixed; color: $color-primary; }
.icon-英语 { background: $color-secondary-fixed; color: $color-secondary; }
.icon-default { background: $color-surface-container; color: $color-on-surface-variant; }
.task-info { flex: 1; }
.task-title-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.task-title { font-family: $font-family; font-size: 20px; font-weight: 600; color: $color-on-surface; }
.task-title-done { text-decoration: line-through; opacity: 0.7; }
.check-circle {
  width: 32px; height: 32px; border-radius: $radius-full;
  background: $color-tertiary; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.check-icon { color: $color-on-tertiary; font-size: 18px; }
.empty-circle {
  width: 32px; height: 32px; border-radius: $radius-full;
  border: 2px solid $color-outline-variant; flex-shrink: 0;
}
.task-desc { font-size: $font-body-md; color: $color-on-surface-variant; display: block; }
.task-desc-done { text-decoration: line-through; opacity: 0.7; }

.task-action { display: flex; align-items: center; }
.action-btn {
  display: flex; align-items: center; justify-content: center;
  min-height: $touch-min; padding: 0 $spacing-md; border-radius: $radius-xl;
  font-family: $font-family; font-size: $font-body-md; font-weight: 600;
}
.btn-start { background: $color-primary; }
.btn-done { background: $color-tertiary; }
.action-btn-text { color: #fff; }
.action-wait { font-size: $font-body-md; color: $color-primary; font-weight: 500; }

.empty-state { padding: 48px 0; text-align: center; }
.empty-text { font-size: $font-body-lg; color: $color-on-surface-variant; }

.celebration {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.7); display: flex; flex-direction: column;
  align-items: center; justify-content: center; z-index: 999;
}
.celebration-emoji { font-size: 80px; }
.celebration-text { font-family: $font-family; font-size: $font-card-title; font-weight: 700; color: #fff; margin-top: $spacing-md; }

.bottom-spacer { height: 100px; }

.bottom-nav {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 100;
  background: #fff; border-top: 2px solid #f1f5f9;
  border-top-left-radius: 32px; border-top-right-radius: 32px;
  display: flex; justify-content: space-around; align-items: center;
  height: 80px; padding-top: 12px; padding-left: $spacing-md; padding-right: $spacing-md;
}
.nav-item {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 8px 32px; color: #94a3b8;
}
.nav-item-active {
  background: #dbeafe; color: #2563eb; border-radius: $radius-2xl;
  box-shadow: inset 0 -2px 0 0 rgba(58,134,255,0.3);
}
.nav-icon { font-size: 24px; margin-bottom: 4px; }
.nav-label { font-family: $font-family; font-size: 12px; font-weight: 500; }
</style>
