<template>
  <view class="page">
    <!-- AppBar -->
    <view class="appbar" :style="{ paddingTop: Math.max(statusBarHeight, 12) + 'px' }">
      <view class="appbar-left">
        <view class="avatar-circle">
          <text class="material-symbols-outlined avatar-icon">person</text>
        </view>
        <text class="appbar-title">我的作业</text>
      </view>
      <view class="appbar-logout" @tap="showLogoutConfirm = true">
        <text class="material-symbols-outlined logout-icon">logout</text>
      </view>
    </view>

    <scroll-view scroll-y class="main" :style="{ paddingTop: (Math.max(statusBarHeight, 12) + 56) + 'px' }">
      <!-- Progress Card: Mint-green organic shape -->
      <view class="progress-card">
        <view class="progress-card-content">
          <text class="progress-greeting">你好！</text>
          <text class="progress-fraction">{{ doneCount }}/{{ tasks.length }} 已完成</text>
          <!-- Linear Progress Bar -->
          <view class="progress-bar-track">
            <view class="progress-bar-fill" :style="{ width: (progressRatio * 100) + '%' }"></view>
          </view>
        </view>
        <!-- Decorative organic blob -->
        <view class="progress-deco"></view>
      </view>

      <!-- Dictation CTA: Pastel-blue organic shape -->
      <view v-if="dictationTask" class="dictation-cta" @tap="goDictationContinuous">
        <view class="cta-content">
          <view class="cta-icon-box">
            <text class="material-symbols-outlined cta-icon">mic</text>
          </view>
          <view class="cta-text">
            <text class="cta-title">听写作业</text>
            <text class="cta-sub">点击开始今日听写</text>
          </view>
          <text class="material-symbols-outlined cta-arrow">chevron_right</text>
        </view>
        <!-- Decorative organic blob -->
        <view class="cta-deco"></view>
      </view>

      <!-- Task List -->
      <view class="task-section">
        <text class="section-title">今日作业</text>
        <view v-if="tasks.length === 0" class="empty-state">
          <text class="empty-text">今天没有任务，休息一下吧！</text>
        </view>
        <view v-for="task in tasks" :key="task.id" :class="['task-card', `card-${task.subject || 'default'}`, (task.status === 'graded' || task.status === 'submitted') ? 'task-done' : '']">
          <!-- Card header: icon + title + badge -->
          <view class="task-card-header">
            <view class="task-header-left">
              <view :class="['task-icon-circle', `icon-${task.subject || 'default'}`]">
                <text class="material-symbols-outlined task-icon">{{ subjectIcon(task.subject) }}</text>
              </view>
              <text :class="['task-title', `title-${task.subject || 'default'}`]">{{ task.title }}</text>
              <view v-if="task.has_dictation" class="dictation-badge">
                <text class="material-symbols-outlined badge-icon">mic</text>
                <text class="badge-text">听写</text>
              </view>
            </view>
            <view :class="['status-badge', `status-${task.status}`]">
              <text class="status-text">{{ statusLabel(task.status) }}</text>
            </view>
          </view>

          <!-- Content area -->
          <view class="task-content-area">
            <text v-if="task.desc" :class="['task-desc', `desc-${task.subject || 'default'}`]">{{ task.desc }}</text>

            <!-- Dictation words preview -->
            <view v-if="task.has_dictation && task.status !== 'graded'" class="dictation-preview">
              <view class="dictation-words-loading" v-if="!taskDictationWords[task.id]">
                <text>加载中...</text>
              </view>
              <view class="dictation-words" v-else>
                <text :class="['dictation-word', `word-${task.subject || 'default'}`]" v-for="(word, i) in taskDictationWords[task.id]" :key="i">{{ word }}</text>
              </view>
            </view>
          </view>

          <!-- Action button -->
          <view class="task-action">
            <view v-if="task.status === 'pending'" class="action-row">
              <view v-if="task.has_dictation" :class="['action-pill', `pill-${task.subject || 'default'}`]" @tap.stop="goDictation(task)">
                <text class="material-symbols-outlined pill-icon">mic</text>
                <text :class="['pill-text', `pill-text-${task.subject || 'default'}`]">开始听写</text>
              </view>
              <view v-else :class="['action-pill', `pill-${task.subject || 'default'}`]" @tap.stop="startTask(task)">
                <text :class="['pill-text', `pill-text-${task.subject || 'default'}`]">开始</text>
              </view>
            </view>
            <view v-if="task.status === 'in_progress'" class="action-row">
              <view :class="['action-pill', `pill-${task.subject || 'default'}`]" @tap.stop="doneTask(task)">
                <text :class="['pill-text', `pill-text-${task.subject || 'default'}`]">完成</text>
              </view>
              <view v-if="task.has_dictation" :class="['action-pill', `pill-${task.subject || 'default'}`]" @tap.stop="goDictation(task)">
                <text class="material-symbols-outlined pill-icon">mic</text>
                <text :class="['pill-text', `pill-text-${task.subject || 'default'}`]">继续听写</text>
              </view>
            </view>
            <view v-if="task.status === 'submitted'" class="action-row">
              <view :class="['action-pill', `pill-${task.subject || 'default'}`]" @tap.stop="cancelSubmit(task)">
                <text :class="['pill-text', `pill-text-${task.subject || 'default'}`]">取消提交</text>
              </view>
            </view>
            <view v-if="task.status === 'graded'" class="action-row">
              <view class="action-pill-completed">
                <text class="pill-text-completed">已完成 ✓</text>
              </view>
            </view>
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

    <!-- 取消提交确认弹窗 -->
    <ConfirmModal
      v-model:visible="showCancelConfirm"
      type="warning"
      icon="undo"
      title="取消提交"
      desc="确定要取消提交吗？取消后可以重新完成作业。"
      cancel-text="再想想"
      confirm-text="确定取消"
      @confirm="confirmCancel"
    />

    <!-- 退出登录确认弹窗 -->
    <ConfirmModal
      v-model:visible="showLogoutConfirm"
      type="warning"
      icon="logout"
      title="退出登录"
      desc="确定要退出当前账号吗？"
      cancel-text="取消"
      confirm-text="退出"
      flat
      @confirm="handleLogout"
    />

    <!-- Bottom Nav -->
    <BottomNav active="home" :navItems="studentNavItems" />
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useTasksStore } from '@/stores/tasks'
import { useSyncStore } from '@/stores/sync'
import { useAuthStore } from '@/stores/auth'
import { getDictationItems } from '@/api/dictation'
import type { TaskOut } from '@/api/tasks'
import BottomNav from '@/components/BottomNav.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import type { NavItem } from '@/components/BottomNav.vue'

const studentNavItems: NavItem[] = [
  { key: 'home', icon: 'assignment', label: '作业', url: '/pages/student/home' },
  { key: 'history', icon: 'history', label: '历史', url: '/pages/parent/grading' },
]

const tasksStore = useTasksStore()
const syncStore = useSyncStore()
const authStore = useAuthStore()
const statusBarHeight = ref(0)
const safeAreaBottom = ref(0)
const showCelebration = ref(false)
const showCancelConfirm = ref(false)
const showLogoutConfirm = ref(false)
const cancelTarget = ref<TaskOut | null>(null)
const taskDictationWords = reactive<Record<string, string[]>>({})

const tasks = computed(() => {
  const list = [...tasksStore.tasks]
  return list.sort((a, b) => {
    const aWeight = (a.status === 'graded' || a.status === 'submitted') ? 1 : 0
    const bWeight = (b.status === 'graded' || b.status === 'submitted') ? 1 : 0
    return aWeight - bWeight
  })
})
const doneCount = computed(() => tasks.value.filter(t => t.status === 'graded' || t.status === 'submitted').length)
const progressRatio = computed(() => tasks.value.length === 0 ? 0 : doneCount.value / tasks.value.length)
const dictationTask = computed(() => tasks.value.find(t => t.has_dictation && t.status !== 'graded'))

function subjectIcon(subject: string | null) {
  const map: Record<string, string> = { '语文': 'menu_book', '数学': 'calculate', '英语': 'translate', '科学': 'science' }
  return map[subject || ''] || 'assignment'
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    'pending': '未完成',
    'in_progress': '进行中',
    'submitted': '已提交',
    'graded': '已完成',
  }
  return map[status] || status
}

async function loadDictationWords(task: TaskOut) {
  if (!task.has_dictation || taskDictationWords[task.id]) return
  try {
    const items = await getDictationItems(task.id)
    taskDictationWords[task.id] = items.map(i => i.content)
  } catch {
    taskDictationWords[task.id] = []
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

async function cancelSubmit(task: TaskOut) {
  cancelTarget.value = task
  showCancelConfirm.value = true
}

async function confirmCancel() {
  showCancelConfirm.value = false
  if (cancelTarget.value) {
    await tasksStore.updateStatus(cancelTarget.value.id, 'in_progress')
  }
  cancelTarget.value = null
}

function handleLogout() {
  authStore.logout()
}

function goDictation(task: TaskOut | undefined) {
  if (!task) return
  uni.navigateTo({ url: `/pages/student/dictation?taskId=${task.id}` })
}

function goDictationContinuous() {
  const sortedDictationTasks = tasks.value
    .filter(t => t.has_dictation && t.status !== 'graded')
    .sort((a, b) => {
      const pa = a.date.split('-'), pb = b.date.split('-')
      const da = pa.length === 3 ? new Date(Number(pa[0]), Number(pa[1]) - 1, Number(pa[2])) : new Date(a.date)
      const db = pb.length === 3 ? new Date(Number(pb[0]), Number(pb[1]) - 1, Number(pb[2])) : new Date(b.date)
      return da.getTime() - db.getTime()
    })

  if (sortedDictationTasks.length === 0) return

  const taskIds = sortedDictationTasks.map(t => t.id).join(',')
  uni.navigateTo({ url: `/pages/student/dictation?taskIds=${taskIds}&continuous=1` })
}

// Load dictation words for tasks that have dictation
watch(tasks, (newTasks) => {
  newTasks.forEach(task => {
    if (task.has_dictation && task.status !== 'graded') {
      loadDictationWords(task)
    }
  })
}, { immediate: true })

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
  font-weight: normal; font-style: normal; line-height: 1;
  letter-spacing: normal; text-transform: none; display: inline-block;
  white-space: nowrap; word-wrap: normal; direction: ltr;
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.page { min-height: 100vh; background: $color-organic-bg; font-family: 'Inter', sans-serif; }

// ═══════════════════════════════════════════════════
// AppBar
// ═══════════════════════════════════════════════════
.appbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: rgba(248, 249, 251, 0.9); backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: space-between;
  padding-left: $spacing-margin; padding-right: $spacing-margin; padding-bottom: 12px;
}
.appbar-left { display: flex; align-items: center; gap: 12px; }
.avatar-circle {
  width: 40px; height: 40px; border-radius: $radius-full;
  background: rgba($color-mint-green-bright, 0.5);
  display: flex; align-items: center; justify-content: center;
}
.avatar-icon { font-size: 20px; color: $color-dark-green; }
.appbar-title { font-size: 20px; font-weight: 700; color: $color-organic-on-surface; letter-spacing: -0.02em; }
.appbar-logout {
  width: 40px; height: 40px; border-radius: $radius-full;
  display: flex; align-items: center; justify-content: center;
  &:active { background: rgba($color-organic-surface-variant, 0.3); }
}
.logout-icon { font-size: 24px; color: $color-organic-text-secondary; }

.main { flex: 1; padding: 0 $spacing-margin; box-sizing: border-box; width: 100%; }

// ═══════════════════════════════════════════════════
// Progress Card (Mint-green organic shape)
// ═══════════════════════════════════════════════════
.progress-card {
  background: $color-mint-green-bright;
  border-radius: 40px 10px 40px 10px;
  padding: 32px;
  box-shadow: $shadow-soft;
  position: relative; overflow: hidden;
  margin-bottom: $spacing-md;
}
.progress-card-content { position: relative; z-index: 1; }
.progress-greeting {
  font-family: 'Inter', sans-serif; font-size: 32px; font-weight: 700;
  color: $color-dark-green; display: block; margin-bottom: 8px;
}
.progress-fraction {
  font-size: 14px; font-weight: 500; color: $color-dark-green;
  display: block; margin-bottom: 12px; opacity: 0.8;
}
.progress-bar-track {
  height: 8px; width: 100%;
  background: rgba($color-dark-green, 0.1); border-radius: $radius-full;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%; background: rgba($color-dark-green, 0.2);
  border-radius: $radius-full; transition: width 0.5s ease;
}
.progress-deco {
  position: absolute; right: -32px; top: -32px;
  width: 128px; height: 128px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
}

// ═══════════════════════════════════════════════════
// Dictation CTA (Pastel-blue organic shape)
// ═══════════════════════════════════════════════════
.dictation-cta {
  background: #819af2;
  border-radius: 10px 40px 10px 40px;
  padding: 24px;
  box-shadow: $shadow-soft;
  margin-bottom: $spacing-lg;
  position: relative; overflow: hidden;
  transition: transform 0.15s;
  &:active { transform: scale(0.98); }
}
.cta-content {
  display: flex; align-items: center; position: relative; z-index: 1;
}
.cta-icon-box {
  width: 48px; height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
  display: flex; align-items: center; justify-content: center;
  margin-right: 16px; flex-shrink: 0;
}
.cta-icon { font-size: 24px; color: #fff; }
.cta-text { flex: 1; display: flex; flex-direction: column; }
.cta-title { font-size: 20px; font-weight: 700; color: #fff; }
.cta-sub { font-size: 14px; color: rgba(255, 255, 255, 0.8); margin-top: 4px; }
.cta-arrow { font-size: 24px; color: rgba(255, 255, 255, 0.7); }
.cta-deco {
  position: absolute; left: -16px; bottom: -32px;
  width: 96px; height: 96px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
}

// ═══════════════════════════════════════════════════
// Task Section
// ═══════════════════════════════════════════════════
.task-section { display: flex; flex-direction: column; gap: $spacing-md; }
.section-title {
  font-size: 24px; font-weight: 700; color: $color-organic-on-surface;
  display: block; margin-bottom: 4px;
}

// ═══════════════════════════════════════════════════
// Task Cards (Subject-colored backgrounds)
// ═══════════════════════════════════════════════════
.task-card {
  border-radius: 32px; padding: 20px;
  box-shadow: $shadow-soft;
  display: flex; flex-direction: column;
  position: relative; overflow: hidden;
}
.task-done { opacity: 0.7; }

// Subject backgrounds
.card-语文 { background: $color-soft-lilac; }
.card-数学 { background: $color-pale-peach; }
.card-英语 { background: $color-mint-green-bright; }
.card-default { background: $color-organic-surface-container; }

// ═══════════════════════════════════════════════════
// Task Card Header
// ═══════════════════════════════════════════════════
.task-card-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 16px;
}
.task-header-left { display: flex; align-items: center; gap: 12px; overflow: hidden; }
.task-icon-circle {
  width: 40px; height: 40px; border-radius: $radius-full;
  background: rgba(255, 255, 255, 0.5);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.icon-语文 .task-icon { color: #581c87; }
.icon-数学 .task-icon { color: #9a3412; }
.icon-英语 .task-icon { color: $color-dark-green; }
.icon-default .task-icon { color: $color-organic-on-surface-variant; }
.task-icon { font-size: 20px; }

.task-title { font-size: 20px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex-shrink: 1; min-width: 0; }
.title-语文 { color: #3b0764; }
.title-数学 { color: #7c2d12; }
.title-英语 { color: $color-dark-green; }
.title-default { color: $color-organic-on-surface; }

// Dictation badge
.dictation-badge {
  display: inline-flex; align-items: center; gap: 2px;
  background: rgba($color-dark-green, 0.8);
  padding: 2px 8px; border-radius: 4px;
}
.badge-icon { font-size: 12px; color: #fff; }
.badge-text { font-size: 10px; font-weight: 600; color: #fff; }

// Status badge
.status-badge {
  padding: 4px 12px; border-radius: $radius-full;
  background: rgba(255, 255, 255, 0.6);
  flex-shrink: 0;
}
.status-text { font-size: 12px; font-weight: 500; }
.status-pending .status-text { color: $color-organic-on-surface-variant; }
.status-in_progress .status-text { color: $color-organic-secondary; }
.status-submitted .status-text { color: $color-primary; }
.status-graded .status-text { color: $color-dark-green; }

// ═══════════════════════════════════════════════════
// Task Content Area (white/40 inner area)
// ═══════════════════════════════════════════════════
.task-content-area {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 16px; padding: 16px;
  margin-bottom: 16px;
}
.task-desc { font-size: 14px; line-height: 1.6; display: block; }
.desc-语文 { color: #581c87; }
.desc-数学 { color: #9a3412; }
.desc-英语 { color: $color-dark-green; }
.desc-default { color: $color-organic-on-surface-variant; }

// Dictation preview
.dictation-preview { margin-top: 12px; }
.dictation-words-loading { font-size: 12px; color: $color-organic-on-surface-variant; }
.dictation-words { display: flex; flex-wrap: wrap; gap: 8px; }
.dictation-word {
  padding: 4px 12px; border-radius: 8px;
  font-size: 14px; font-weight: 500;
  background: rgba(255, 255, 255, 0.6);
}
.word-语文 { color: #581c87; }
.word-数学 { color: #9a3412; }
.word-英语 { color: $color-dark-green; }
.word-default { color: $color-organic-on-surface; }

// ═══════════════════════════════════════════════════
// Action Buttons (semi-transparent white pill)
// ═══════════════════════════════════════════════════
.task-action { display: flex; align-items: center; }
.action-row { display: flex; gap: $spacing-sm; width: 100%; }

.action-pill {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 14px 0; border-radius: $radius-full;
  background: rgba(255, 255, 255, 0.7);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.15s;
  &:active { background: rgba(255, 255, 255, 0.9); transform: scale(0.98); }
}
.pill-icon { font-size: 18px; }
.pill-text { font-size: 16px; font-weight: 700; }
.pill-text-语文 { color: #581c87; }
.pill-text-数学 { color: #9a3412; }
.pill-text-英语 { color: $color-dark-green; }
.pill-text-default { color: $color-organic-on-surface; }

.action-pill-completed {
  flex: 1; display: flex; align-items: center; justify-content: center;
  padding: 14px 0; border-radius: $radius-full;
  background: rgba(255, 255, 255, 0.4);
}
.pill-text-completed { font-size: 16px; font-weight: 600; color: $color-dark-green; }

// ═══════════════════════════════════════════════════
// Empty & Celebration
// ═══════════════════════════════════════════════════
.empty-state { padding: 48px 0; text-align: center; }
.empty-text { font-size: 18px; color: $color-organic-on-surface-variant; }

.celebration {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7); display: flex; flex-direction: column;
  align-items: center; justify-content: center; z-index: 999;
}
.celebration-emoji { font-size: 80px; }
.celebration-text { font-size: 24px; font-weight: 700; color: #fff; margin-top: $spacing-md; }

.bottom-spacer { height: 100px; }
</style>
