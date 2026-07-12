<template>
  <view class="page">
    <!-- TopAppBar -->
    <view class="appbar" :style="{ paddingTop: Math.max(statusBarHeight, 12) + 'px' }">
      <view class="appbar-left">
        <view class="avatar-circle">
          <text class="material-symbols-outlined">person</text>
        </view>
        <text class="appbar-title">今日作业</text>
      </view>
      <view class="appbar-right" @tap="handleLogout">
        <text class="material-symbols-outlined">logout</text>
      </view>
    </view>

    <!-- Main -->
    <scroll-view scroll-y class="main" :style="{ paddingTop: (appbarHeight + 8) + 'px' }">
      <!-- Hero Progress Card -->
      <view class="hero-card">
        <view class="hero-content">
          <view class="hero-top">
            <text class="material-symbols-outlined hero-icon">mood</text>
            <text class="hero-title">今日作业概览</text>
          </view>
          <text class="hero-body">
            今天共有 <text class="hero-num">{{ tasks.length }}</text> 项作业，已完成
            <text class="hero-num-done">{{ doneCount }}</text> 项。
          </text>
          <view class="progress-section">
            <view class="progress-row">
              <text class="progress-label">整体进度</text>
              <text class="progress-pct">{{ progressPct }}%</text>
            </view>
            <view class="progress-bar-bg">
              <view class="progress-bar-fill" :style="{ width: progressPct + '%' }"></view>
            </view>
          </view>
        </view>
      </view>

      <!-- Family Code -->
      <view class="family-code-card" @tap="copyFamilyCode">
        <view class="family-code-left">
          <text class="material-symbols-outlined family-icon">family_restroom</text>
          <text class="family-label">家庭码:</text>
          <text class="family-code">{{ familyCode }}</text>
        </view>
        <text class="material-symbols-outlined copy-icon">content_copy</text>
      </view>

      <!-- Pending Tasks -->
      <view class="section">
        <text class="section-label">待完成 ({{ pendingTasks.length }})</text>
        <view v-for="task in pendingTasks" :key="task.id" class="task-card">
          <!-- Task Header -->
          <view class="task-header">
            <view :class="['task-icon-circle', `icon-bg-${task.subject || 'default'}`]">
              <text class="material-symbols-outlined task-icon">{{ subjectIcon(task.subject) }}</text>
            </view>
            <text class="task-title">{{ task.title }}</text>
            <view v-if="task.has_dictation" class="badge badge-dictation">
              <text class="material-symbols-outlined badge-icon">record_voice_over</text>
              <text class="badge-text">听写</text>
            </view>
            <view :class="['badge', `badge-${task.status}`]">
              <text class="badge-text">{{ statusLabel(task.status) }}</text>
            </view>
          </view>

          <!-- Task Content -->
          <view :class="['task-content', `content-bg-${task.subject || 'default'}`]">
            <text class="content-date">{{ formatDate(task.date) }}</text>
            <view v-if="task.desc" class="content-body">
              <text class="content-desc" v-for="(line, i) in descLines(task.desc)" :key="i">{{ line }}</text>
            </view>
          </view>

          <!-- Task Actions -->
          <view class="task-actions">
            <view v-if="task.has_dictation" :class="['action-btn', `action-bg-${task.subject || 'default'}`]" @tap="previewDictation(task)">
              <text class="material-symbols-outlined action-icon">visibility</text>
              <text class="action-text">预览听写</text>
            </view>
            <view :class="['action-btn', `action-bg-${task.subject || 'default'}`, task.has_dictation ? 'action-btn-flex' : '']" @tap="editTask(task)">
              <text class="material-symbols-outlined action-icon">edit</text>
              <text class="action-text">编辑</text>
            </view>
          </view>
        </view>
        <view v-if="pendingTasks.length === 0" class="empty-hint">
          <text class="empty-hint-text">暂无待完成任务 🎉</text>
        </view>
      </view>

      <!-- Divider -->
      <view v-if="doneTasks.length > 0" class="section-divider"></view>

      <!-- Completed Tasks -->
      <view v-if="doneTasks.length > 0" class="section">
        <text class="section-label section-label-done">已完成 ({{ doneTasks.length }})</text>
        <view v-for="task in doneTasks" :key="task.id" class="task-card task-card-done">
          <view class="task-header">
            <view :class="['task-icon-circle', `icon-bg-${task.subject || 'default'}`, 'icon-done']">
              <text class="material-symbols-outlined task-icon">{{ subjectIcon(task.subject) }}</text>
            </view>
            <text class="task-title task-title-done">{{ task.title }}</text>
            <view class="badge badge-completed">
              <text class="material-symbols-outlined badge-icon-sm">check_circle</text>
              <text class="badge-text">已完成</text>
            </view>
          </view>
          <view class="task-content task-content-done">
            <text class="content-desc content-desc-done">{{ task.desc || '无描述' }}</text>
          </view>
        </view>
      </view>

      <view class="section-divider"></view>
      <view class="section plan-section">
        <text class="section-label">进行中的作业计划 ({{ plansStore.activePlans.length }})</text>
        <text v-if="plansStore.syncWarning" class="plan-warning">{{ plansStore.syncWarning }}</text>
        <view v-if="plansStore.listLoading && !plansStore.activePlans.length" class="empty-hint"><text class="empty-hint-text">正在加载作业计划…</text></view>
        <view v-else-if="!plansStore.activePlans.length" class="empty-hint" @tap="goCreate"><text class="empty-hint-text">暂无进行中的作业计划，去布置</text></view>
        <HomeworkPlanCard v-for="plan in plansStore.activePlans" :key="plan.id" :plan="plan" :busy="plansStore.deleting" @edit="editPlan" @delete="requestDeletePlan" />
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
          <view class="dictation-modal-info">
            <text class="dictation-modal-subtitle">{{ dictationModal.taskTitle }}</text>
            <view class="shuffle-btn" @tap="shuffleWords">
              <text class="material-symbols-outlined shuffle-icon">shuffle</text>
              <text class="shuffle-text">乱序</text>
            </view>
          </view>

          <view v-if="dictationModal.loading" class="dictation-loading">
            <text class="dictation-loading-text">加载中...</text>
          </view>
          <view v-else class="dictation-words-grid">
            <view
              v-for="(word, i) in dictationModal.words"
              :key="i"
              :class="['word-card', playingIndex === i ? 'word-card-playing' : '', i % 2 === 0 ? 'word-card-lilac' : 'word-card-mint']"
              @tap="playWord(word, i)"
            >
              <text class="word-text">{{ word }}</text>
              <view class="word-play-btn">
                <text class="material-symbols-outlined word-play-icon">
                  {{ playingIndex === i ? 'volume_up' : 'play_arrow' }}
                </text>
              </view>
            </view>
          </view>

          <view class="dictation-modal-actions">
            <view class="play-all-btn" @tap="playAllWords">
              <text class="material-symbols-outlined play-all-icon">playlist_play</text>
              <text class="play-all-text">顺序播放</text>
            </view>
          </view>
        </view>
      </view>

      <view class="bottom-spacer"></view>
    </scroll-view>

    <!-- 退出登录确认弹窗 -->
    <ConfirmModal
      v-model:visible="showLogoutConfirm"
      type="warning"
      icon="logout"
      title="退出登录"
      desc="确定要退出吗？"
      cancel-text="取消"
      confirm-text="确定"
      :flat="true"
      @confirm="confirmLogout"
    />

    <ConfirmModal v-model:visible="showDeletePlanConfirm" type="warning" icon="delete" title="删除这个计划？" desc="删除后将停止生成后续作业，已经生成的作业仍会保留。" cancel-text="取消" confirm-text="确认删除" :flat="true" @confirm="confirmDeletePlan" />

    <!-- Bottom Nav -->
    <BottomNav active="dashboard" :navItems="parentNavItems" />
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { useTasksStore } from '@/stores/tasks'
import { useSyncStore } from '@/stores/sync'
import { useHomeworkPlansStore } from '@/stores/homework-plans'
import { getDictationItems } from '@/api/dictation'
import type { TaskOut } from '@/api/tasks'
import { BASE_URL } from '@/api/config'
import BottomNav from '@/components/BottomNav.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import HomeworkPlanCard from '@/components/HomeworkPlanCard.vue'
import type { NavItem } from '@/components/BottomNav.vue'

const parentNavItems: NavItem[] = [
  { key: 'dashboard', icon: 'assignment', label: '作业', url: '/pages/parent/dashboard' },
  { key: 'create', icon: 'calendar_today', label: '布置', url: '/pages/parent/task-create' },
  { key: 'grading', icon: 'history', label: '历史', url: '/pages/parent/grading' },
]

const authStore = useAuthStore()
const tasksStore = useTasksStore()
const syncStore = useSyncStore()
const plansStore = useHomeworkPlansStore()
const familyCode = ref('加载中')

const statusBarHeight = ref(0)
const safeAreaBottom = ref(0)
const appbarHeight = ref(88)

// Dictation preview
const dictationModal = reactive({
  visible: false,
  loading: false,
  taskId: '',
  taskTitle: '',
  words: [] as string[],
})
const playingIndex = ref(-1)
const showLogoutConfirm = ref(false)
const showDeletePlanConfirm = ref(false)
const deletingPlanId = ref('')
function goCreate() { uni.redirectTo({ url: '/pages/parent/task-create' }) }
function editPlan(id: string) { uni.navigateTo({ url: `/pages/parent/homework-plan-edit?id=${id}` }) }
function requestDeletePlan(id: string) { deletingPlanId.value = id; showDeletePlanConfirm.value = true }
async function confirmDeletePlan() {
  if (!deletingPlanId.value) return
  try { await plansStore.deletePlan(deletingPlanId.value); uni.showToast({ title: '计划已删除，已有作业不受影响', icon: 'none' }) }
  catch (e: any) { uni.showToast({ title: e.message || '删除失败', icon: 'none' }) }
  finally { deletingPlanId.value = '' }
}

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

function copyFamilyCode() {
  uni.setClipboardData({
    data: familyCode.value,
    success: () => uni.showToast({ title: '已复制家庭码', icon: 'success' })
  })
}

function handleLogout() {
  showLogoutConfirm.value = true
}

function confirmLogout() {
  authStore.logout()
  uni.reLaunch({ url: '/pages/auth/login' })
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
  const map: Record<string, string> = { '语文': 'menu_book', '数学': 'calculate', '英语': 'language', '科学': 'science' }
  return map[subject || ''] || 'assignment'
}

function statusLabel(status: string) {
  const map: Record<string, string> = { 'pending': '未开始', 'in_progress': '进行中', 'submitted': '已提交', 'graded': '已批改' }
  return map[status] || status
}

function formatDate(dateStr: string) {
  const parts = dateStr.split('-')
  const d = parts.length === 3
    ? new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]))
    : new Date(dateStr)
  const weekDays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const wd = weekDays[d.getDay()]
  return `${d.getFullYear()}.${m}.${day}${wd}练习:`
}

function descLines(desc: string | null) {
  if (!desc) return []
  return desc.split('\n').filter(l => l.trim())
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

function shuffleWords() {
  const words = [...dictationModal.words]
  for (let i = words.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [words[i], words[j]] = [words[j], words[i]]
  }
  dictationModal.words = words
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
    try {
      if (dashboardAudioContext) {
        dashboardAudioContext.destroy()
      }
      const url = getTTSAudioUrl(text)
      dashboardAudioContext = uni.createInnerAudioContext()
      dashboardAudioContext.volume = 1.0
      dashboardAudioContext.src = url

      dashboardAudioContext.onCanplay(() => {
        dashboardAudioContext?.play()
      })
      dashboardAudioContext.onEnded(() => {
        dashboardAudioContext?.destroy()
        dashboardAudioContext = null
        resolve()
      })
      dashboardAudioContext.onError(() => {
        dashboardAudioContext?.destroy()
        dashboardAudioContext = null
        resolve()
      })
    } catch {
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

onMounted(() => {
  const info = uni.getSystemInfoSync()
  statusBarHeight.value = info.statusBarHeight || 0
  safeAreaBottom.value = info.safeAreaInsets?.bottom || 0
  appbarHeight.value = Math.max(statusBarHeight.value, 12) + 56 + 12
  tasksStore.loadCached()
  loadFamilyCode()
})

onShow(async () => {
  try { await plansStore.materialize() }
  catch { plansStore.syncWarning = '计划作业同步失败，请稍后重试' }
  await Promise.allSettled([tasksStore.fetchTodayTasks(), plansStore.fetchActivePlans()])
  if (plansStore.syncWarning) uni.showToast({ title: plansStore.syncWarning, icon: 'none' })
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

.page { min-height: 100vh; background: $color-organic-bg; font-family: 'Inter', $font-family-body; }

// ─── TopAppBar ───
.appbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: #fff; border-bottom: none;
  display: flex; align-items: center; justify-content: space-between;
  padding-left: $spacing-margin; padding-right: $spacing-margin;
  padding-bottom: 12px; padding-top: 12px;
  min-height: 64px; box-sizing: border-box;
}
.appbar-left { display: flex; align-items: center; gap: $spacing-sm; }
.avatar-circle {
  width: 40px; height: 40px; border-radius: $radius-full;
  background: $color-mint-light; display: flex; align-items: center; justify-content: center;
  color: $color-dark-green;
}
.appbar-title { font-family: 'Inter', sans-serif; font-size: 24px; font-weight: 600; color: $color-dark-green; line-height: 32px; }
.appbar-right {
  width: 40px; height: 40px; border-radius: $radius-full;
  display: flex; align-items: center; justify-content: center;
  color: $color-dark-green; opacity: 0.6;
  &:active { opacity: 1; background: $color-mint-light; }
}

// ─── Main Scroll Area ───
.main { flex: 1; padding-left: $spacing-margin; padding-right: $spacing-margin; box-sizing: border-box; width: 100%; }

// ─── Hero Card ───
.hero-card {
  background: $color-mint-light;
  border-radius: 40px 120px 40px 120px;
  padding: 32px; margin-bottom: 16px;
  position: relative; overflow: hidden;
  box-shadow: 0 4px 16px rgba(29, 59, 22, 0.08);
}
.hero-content { position: relative; z-index: 1; }
.hero-top { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.hero-icon { color: $color-dark-green; font-size: 24px; }
.hero-title { font-family: 'Inter', sans-serif; font-size: 24px; font-weight: 700; color: $color-dark-green; line-height: 32px; }
.hero-body { font-size: 14px; color: rgba(29, 59, 22, 0.8); display: block; margin-bottom: 24px; font-weight: 500; line-height: 20px; }
.hero-num { font-weight: 700; font-size: 18px; color: $color-dark-green; }
.hero-num-done { font-weight: 700; font-size: 18px; color: $color-dark-green; }
.progress-section { display: flex; flex-direction: column; gap: 8px; }
.progress-row { display: flex; justify-content: space-between; align-items: center; }
.progress-label { font-size: 12px; color: rgba(29, 59, 22, 0.8); font-weight: 600; }
.progress-pct { font-size: 14px; color: $color-dark-green; font-weight: 700; }
.progress-bar-bg {
  width: 100%; height: 12px; background: rgba(29, 59, 22, 0.1);
  border-radius: $radius-full; overflow: hidden;
}
.progress-bar-fill { height: 100%; background: $color-dark-green; border-radius: $radius-full; transition: width 0.3s; }

// ─── Family Code Card ───
.family-code-card {
  display: flex; align-items: center; justify-content: space-between;
  background: rgba(255, 255, 255, 0.5); border-radius: 24px;
  padding: 16px; margin-bottom: 24px;
  border: 1px solid rgba($color-organic-outline-variant, 0.1);
}
.family-code-left { display: flex; align-items: center; gap: 8px; }
.family-icon { font-size: 20px; color: rgba(29, 59, 22, 0.6); }
.family-label { font-size: 12px; color: rgba(29, 59, 22, 0.7); font-weight: 500; }
.family-code { font-size: 14px; color: $color-dark-green; font-weight: 700; letter-spacing: 2px; }
.copy-icon { font-size: 18px; color: rgba(29, 59, 22, 0.6); }

// ─── Section ───
.section { margin-bottom: 24px; }
.section-label {
  font-family: 'Inter', sans-serif; font-size: 18px; font-weight: 700;
  color: $color-dark-green; display: block; margin-bottom: 24px;
  line-height: 24px;
}
.section-label-done { color: $color-organic-on-surface-variant; }
.section-divider { height: 1px; background: rgba($color-organic-outline-variant, 0.3); margin: 8px 0; }

.plan-section { margin-top: 24px; }
.plan-warning { display:block; margin:-12px 0 16px; padding:10px 12px; border-radius:12px; background:#fff4dc; color:#765b12; font-size:12px; }

// ─── Task Card ───
.task-card {
  background: $color-organic-surface-container-lowest;
  border-radius: 24px; padding: 24px;
  box-shadow: 0px 12px 32px rgba(0, 0, 0, 0.06);
  margin-bottom: 16px;
  display: flex; flex-direction: column; gap: 16px;
}
.task-card-done {
  background: $color-organic-surface-container-high;
  opacity: 0.8;
}

// Task Header
.task-header { display: flex; align-items: center; gap: 8px; }
.task-icon-circle {
  width: 30px; height: 30px; border-radius: $radius-full;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.icon-bg-语文 { background: $color-soft-lilac; color: #4e453c; }
.icon-bg-数学 { background: $color-pale-peach; color: #4e453c; }
.icon-bg-英语 { background: $color-mint-green-bright; color: $color-dark-green; }
.icon-bg-科学 { background: $color-soft-lilac; color: $color-dark-green; }
.icon-bg-default { background: $color-organic-surface-container; color: $color-organic-on-surface-variant; }
.icon-done { opacity: 0.6; }

.task-icon { font-size: 15px; }
.task-title {
  font-family: 'Inter', sans-serif; font-size: 16px; font-weight: 700;
  color: $color-dark-green; line-height: 22px; flex: 1; min-width: 0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.task-title-done { text-decoration: line-through; color: rgba(29, 59, 22, 0.6); }

// Badges
.badge {
  display: inline-flex; align-items: center; gap: 3px;
  padding: 4px 10px; border-radius: $radius-full;
  font-size: 12px; font-weight: 700; line-height: 16px; flex-shrink: 0;
}
.badge-dictation { background: $color-on-secondary-fixed-variant; color: #fff; }
.badge-pending { background: $color-organic-surface-variant; color: $color-organic-on-surface-variant; font-weight: 600; }
.badge-in_progress { background: $color-pale-peach; color: $color-organic-on-surface-variant; font-weight: 600; }
.badge-completed { background: rgba($color-mint-light, 0.6); color: $color-dark-green; font-weight: 600; }
.badge-icon { font-size: 13px; }
.badge-icon-sm { font-size: 13px; }
.badge-text { color: inherit; font-size: 12px; font-weight: 600; }

// Task Content
.task-content {
  border-radius: 16px; padding: 20px;
  font-size: 14px; color: $color-organic-on-surface-variant;
}
.content-bg-语文 { background: rgba($color-soft-lilac, 0.3); }
.content-bg-数学 { background: rgba($color-pale-peach, 0.3); }
.content-bg-英语 { background: $color-mint-light; }
.content-bg-科学 { background: rgba($color-soft-lilac, 0.3); }
.content-bg-default { background: $color-organic-surface-container; }

.content-date {
  font-weight: 700; color: $color-dark-green; display: block;
  margin-bottom: 12px; letter-spacing: 1px; font-size: 14px;
}
.content-body { display: flex; flex-direction: column; gap: 12px; }
.content-desc {
  color: rgba(29, 59, 22, 0.9); font-weight: 500; font-size: 14px; line-height: 20px;
}
.content-desc-done { text-decoration: line-through; color: rgba(29, 59, 22, 0.6); }
.task-content-done { background: rgba($color-organic-surface-container, 0.5); }

// Task Actions
.task-actions { display: flex; gap: 12px; }
.action-btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 12px 0; border-radius: $radius-full;
  font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 700;
  color: $color-organic-on-surface-variant;
  &:active { opacity: 0.8; transform: scale(0.98); }
}
.action-bg-语文 { background: $color-soft-lilac; }
.action-bg-数学 { background: $color-pale-peach; }
.action-bg-英语 { background: $color-mint-green-bright; color: $color-dark-green; }
.action-bg-科学 { background: $color-soft-lilac; }
.action-bg-default { background: $color-organic-surface-variant; }
.action-btn-flex { flex: 1; }
.action-icon { font-size: 20px; }
.action-text { color: inherit; font-size: 14px; font-weight: 700; }

.empty-hint { padding: $spacing-md; text-align: center; }
.empty-hint-text { color: $color-organic-on-surface-variant; font-size: 14px; }
.bottom-spacer { height: 120px; }

// ─── Dictation Preview Modal (Organic Style) ───
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(28, 27, 28, 0.2); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  z-index: 999; padding: $spacing-margin;
}
.dictation-modal {
  background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(12px);
  border-radius: 32px; width: 100%; max-width: 360px;
  padding: 24px; padding-bottom: 48px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.4);
  position: relative;
}
.dictation-modal-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 16px;
}
.dictation-modal-title {
  font-family: 'Inter', sans-serif; font-size: 24px; font-weight: 600;
  color: $color-organic-primary;
}
.close-btn {
  width: 36px; height: 36px; border-radius: $radius-full;
  display: flex; align-items: center; justify-content: center;
  color: $color-organic-text-secondary;
}
.dictation-modal-info {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16px;
}
.dictation-modal-subtitle {
  font-size: 14px; color: $color-organic-text-secondary;
}
.shuffle-btn {
  display: flex; align-items: center; gap: 4px;
  background: rgba($color-organic-surface-container-highest, 0.5);
  padding: 6px 12px; border-radius: $radius-full;
  font-size: 13px; font-weight: 500; color: $color-organic-primary;
}
.shuffle-icon { font-size: 18px; }
.shuffle-text { font-size: 13px; font-weight: 500; }

.dictation-loading { padding: 32px; text-align: center; }
.dictation-loading-text { color: $color-organic-on-surface-variant; font-size: 14px; }

// Words Grid - Organic card style
.dictation-words-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
}
.word-card {
  padding: 14px; display: flex; align-items: center; justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
  &:active { transform: scale(0.97); }
}
.word-card-lilac { background: rgba($color-soft-lilac, 0.4); border-radius: 65% 35% 58% 42% / 47% 41% 59% 53%; }
.word-card-mint { background: rgba($color-mint-green, 0.4); border-radius: 45% 55% 42% 58% / 54% 48% 52% 46%; }
.word-card-playing { box-shadow: 0 4px 16px rgba(29, 59, 22, 0.15); }

.word-text {
  font-family: 'Inter', sans-serif; font-size: 18px; font-weight: 600;
  color: $color-organic-primary; margin-left: 8px;
}
.word-play-btn {
  width: 32px; height: 32px; border-radius: $radius-full;
  background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  display: flex; align-items: center; justify-content: center;
}
.word-play-icon { font-size: 16px; color: $color-organic-primary; }
.word-card-playing .word-play-icon { color: $color-dark-green; }

.dictation-modal-actions {
  position: absolute; bottom: -28px; left: 0; right: 0;
  display: flex; justify-content: center;
}
.play-all-btn {
  width: 85%; background: $color-organic-primary; color: $color-organic-on-primary;
  border-radius: $radius-full; height: 56px;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  &:active { transform: scale(0.98); }
}
.play-all-icon { font-size: 24px; }
.play-all-text { font-family: 'Inter', sans-serif; font-size: 18px; font-weight: 600; color: #fff; }

</style>
