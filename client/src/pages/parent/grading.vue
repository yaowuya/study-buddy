<template>
  <view class="page">
    <!-- Organic Background -->
    <view class="organic-bg">
      <view class="blob blob-1"></view>
      <view class="blob blob-2"></view>
      <view class="blob blob-3"></view>
    </view>

    <!-- Scrollable Content -->
    <scroll-view scroll-y class="main" :style="{ paddingTop: (statusBarHeight + 12) + 'px' }">
      <!-- Header + Filter + Stats -->
      <view class="header-section">
        <view class="header-row">
          <text class="page-title">作业历史</text>
          <view class="filter-wrapper">
            <view class="filter-pill glass-card" @tap="showFilterDropdown = !showFilterDropdown">
              <text class="filter-pill-text">{{ filterLabel }}</text>
              <text class="material-symbols-outlined filter-pill-arrow">expand_more</text>
            </view>
            <view v-if="showFilterDropdown" class="filter-dropdown">
              <view
                v-for="opt in filterOptions"
                :key="opt.value"
                :class="['filter-option', currentFilter === opt.value ? 'filter-option-active' : '']"
                @tap="selectFilter(opt.value)"
              >
                <text class="filter-option-text">{{ opt.label }}</text>
              </view>
            </view>
          </view>
        </view>

        <!-- Statistics Card -->
        <view class="stats-card glass-card">
          <view class="stat-item">
            <text class="stat-label">总任务</text>
            <text class="stat-value stat-total">{{ filteredTasks.length }}</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-label">已完成</text>
            <text class="stat-value stat-pass">{{ passCount }}</text>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <text class="stat-label">待完成</text>
            <text class="stat-value stat-pending">{{ pendingCount }}</text>
          </view>
        </view>
      </view>

      <!-- Empty State -->
      <view v-if="dateGroups.length === 0" class="empty">
        <view class="empty-blob">
          <text class="material-symbols-outlined empty-icon">history</text>
        </view>
        <text class="empty-text">暂无历史记录</text>
      </view>

      <!-- Date Groups -->
      <view v-for="(group, gi) in dateGroups" :key="group.label" class="date-group">
        <!-- Date Header -->
        <view class="date-header">
          <view class="date-pill glass-card">
            <text class="material-symbols-outlined date-pill-icon">stars</text>
            <text class="date-pill-text">{{ group.label }}</text>
          </view>
          <view class="date-line"></view>
        </view>

        <!-- Task Cards -->
        <view
          v-for="(task, ti) in group.tasks"
          :key="task.id"
          :class="['task-card glass-card', getCardColor(gi + ti), (gi + ti) % 2 === 0 ? 'stagger-left' : 'stagger-right']"
        >
          <!-- Card Top: Title + Status Badge -->
          <view class="card-top">
            <text class="card-title">{{ task.title }}</text>
            <view v-if="task.status === 'graded'" :class="['status-badge glass-card', gradedResult[task.id] ? '' : 'badge-fail']">
              <text class="material-symbols-outlined badge-icon">{{ gradedResult[task.id] ? 'emoji_events' : 'smart_toy' }}</text>
              <text class="badge-text">{{ gradedResult[task.id] ? '任务完成' : '不合格' }}</text>
            </view>
          </view>

          <!-- Task Description -->
          <view v-if="task.desc" class="card-desc">
            <text class="desc-text">{{ task.desc }}</text>
          </view>

          <!-- Dictation Words -->
          <view v-if="task.has_dictation && dictationWords[task.id]?.length" class="dictation-section">
            <view class="dictation-words">
              <text v-for="(word, i) in dictationWords[task.id]" :key="i" class="word-pill">{{ word }}</text>
            </view>
          </view>

          <!-- Parent Comment -->
          <view v-if="task.status === 'graded' && gradedComment[task.id]" class="comment-section">
            <view class="comment-bubble">
              <view class="comment-top">
                <text class="material-symbols-outlined comment-icon">chat_bubble</text>
                <text class="comment-label">家长评语</text>
              </view>
              <text class="comment-text">{{ gradedComment[task.id] }}</text>
            </view>
          </view>

          <!-- Grading Buttons (parent mode, submitted tasks) -->
          <view v-if="task.status === 'submitted' && !isStudentMode" class="grade-row">
            <view class="grade-btn btn-fail" @tap="doGradeFail(task)">
              <text class="material-symbols-outlined grade-btn-icon">smart_toy</text>
              <text class="grade-btn-text">需要复习</text>
            </view>
            <view class="grade-btn btn-pass" @tap="doGradePass(task)">
              <text class="material-symbols-outlined grade-btn-icon">emoji_events</text>
              <text class="grade-btn-text">任务完成</text>
            </view>
          </view>

          <!-- Student waiting hint -->
          <view v-if="task.status === 'submitted' && isStudentMode" class="waiting-row">
            <text class="waiting-text">⏳ 等待家长评价</text>
          </view>
        </view>
      </view>

      <view class="bottom-spacer"></view>
    </scroll-view>

    <!-- Family Code Modal -->
    <view v-if="showCode" class="modal-overlay" @tap="showCode = false">
      <view class="family-modal" @tap.stop>
        <view class="family-icon-wrap">
          <text class="material-symbols-outlined family-icon">family_restroom</text>
        </view>
        <text class="family-modal-title">家庭连接码</text>
        <text class="family-code">{{ familyCode }}</text>
        <text class="family-hint">让学生输入此码完成绑定</text>
        <view class="family-close-btn" @tap="showCode = false">
          <text class="family-close-text">知道了</text>
        </view>
      </view>
    </view>

    <!-- Comment Modal -->
    <view v-if="commentModal.visible" class="modal-overlay" @tap="closeCommentModal">
      <view class="comment-modal" @tap.stop>
        <text class="cm-title">添加评语（可选）</text>
        <textarea
          v-model="commentModal.text"
          class="cm-textarea"
          placeholder="写下你的评语…"
          maxlength="100"
        />
        <view class="cm-btns">
          <view class="cm-btn cm-skip" @tap="skipModal">
            <text class="cm-btn-text cm-skip-text">跳过</text>
          </view>
          <view class="cm-btn cm-confirm" @tap="confirmModal">
            <text class="cm-btn-text cm-confirm-text">确认</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Logout Confirm -->
    <ConfirmModal
      v-model:visible="showLogoutConfirm"
      type="warning"
      icon="logout"
      title="退出登录"
      desc="确定要退出登录吗？"
      confirmText="退出"
      cancelText="取消"
      :flat="true"
      @confirm="handleLogout"
    />

    <!-- Bottom Nav -->
    <BottomNav active="grading" :navItems="isStudentMode ? studentNavItems : parentNavItems" />
  </view>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { useTasksStore } from '@/stores/tasks'
import { gradeSubmission, listSubmissions, submitTask as apiSubmitTask } from '@/api/submissions'
import { getDictationItems } from '@/api/dictation'
import type { TaskOut } from '@/api/tasks'
import BottomNav from '@/components/BottomNav.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import type { NavItem } from '@/components/BottomNav.vue'

const parentNavItems: NavItem[] = [
  { key: 'dashboard', icon: 'book', label: '作业', url: '/pages/parent/dashboard' },
  { key: 'create', icon: 'add_circle', label: '布置', url: '/pages/parent/task-create' },
  { key: 'grading', icon: 'history', label: '历史', url: '/pages/parent/grading' },
]

const studentNavItems: NavItem[] = [
  { key: 'home', icon: 'book', label: '作业', url: '/pages/student/home' },
  { key: 'grading', icon: 'history', label: '历史', url: '/pages/parent/grading' },
]

const authStore = useAuthStore()
const tasksStore = useTasksStore()
const showCode = ref(false)
const showLogoutConfirm = ref(false)
const familyCode = ref('加载中')

const statusBarHeight = ref(0)

// 日期筛选
const currentFilter = ref('week')
const showFilterDropdown = ref(false)
const filterOptions = [
  { value: 'today', label: '今日' },
  { value: 'week', label: '本周' },
  { value: 'month', label: '本月' },
  { value: 'year', label: '今年' },
]
const filterLabel = computed(() => filterOptions.find(o => o.value === currentFilter.value)?.label || '本周')

function selectFilter(value: string) {
  currentFilter.value = value
  showFilterDropdown.value = false
  loadTasksForFilter()
}

function formatDate(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function parseDate(dateStr: string): Date {
  // 兼容 Android 真机：避免 new Date("2026-06-15") 返回 Invalid Date
  const parts = dateStr.split('-')
  if (parts.length === 3) {
    return new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]))
  }
  return new Date(dateStr)
}

function loadTasksForFilter() {
  gradedResult && Object.keys(gradedResult).forEach(k => delete gradedResult[k])
  Object.keys(gradedComment).forEach(k => delete gradedComment[k])
  Object.keys(dictationWords).forEach(k => delete dictationWords[k])

  const [rangeStart, rangeEnd] = getDateRange(currentFilter.value)
  const dateFrom = formatDate(rangeStart)
  const dateTo = formatDate(rangeEnd)
  console.log('[grading] loadTasksForFilter called:', { dateFrom, dateTo })
  tasksStore.fetchAllTasks(dateFrom, dateTo).then(loadGradedInfo).catch((err) => {
    console.error('[grading] fetchAllTasks failed:', err)
  })
}

// 是否为学生模式（只读）
const isStudentMode = computed(() => authStore.isStudent())

// taskId -> is_correct
const gradedResult = reactive<Record<string, boolean>>({})
// taskId -> comment
const gradedComment = reactive<Record<string, string>>({})
// taskId -> 听写词语列表
const dictationWords = reactive<Record<string, string[]>>({})
// 提交中的 taskId 集合
const submitting = reactive<Record<string, boolean>>({})

// 评语弹窗状态
const commentModal = reactive({
  visible: false,
  task: null as TaskOut | null,
  isCorrect: false,
  text: '',
})

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

function handleLogout() {
  authStore.logout()
}

function showFamilyCode() {
  showCode.value = true
}

const allTasks = computed(() =>
  (Array.isArray(tasksStore.tasks) ? tasksStore.tasks : [])
    .filter(t => t.status === 'submitted' || t.status === 'graded')
)

function getDateRange(filter: string): [Date, Date] {
  const now = new Date()
  const start = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  let end = new Date(start)
  if (filter === 'today') {
    end = new Date(start)
  } else if (filter === 'week') {
    const day = start.getDay()
    const diff = day === 0 ? -6 : 1 - day // Monday as first day
    start.setDate(start.getDate() + diff)
    end = new Date(start)
    end.setDate(end.getDate() + 6)
  } else if (filter === 'month') {
    start.setDate(1)
    end = new Date(now.getFullYear(), now.getMonth() + 1, 0)
  } else if (filter === 'year') {
    start.setMonth(0, 1)
    end = new Date(now.getFullYear(), 11, 31)
  }
  end.setHours(23, 59, 59, 999)
  return [start, end]
}

const filteredTasks = computed(() => {
  const [rangeStart, rangeEnd] = getDateRange(currentFilter.value)
  return allTasks.value.filter(t => {
    const d = parseDate(t.date)
    return d >= rangeStart && d <= rangeEnd
  })
})

const passCount = computed(() =>
  filteredTasks.value.filter(t => t.status === 'graded' && gradedResult[t.id]).length
)

const pendingCount = computed(() =>
  filteredTasks.value.filter(t => t.status === 'submitted').length
)

const dateGroups = computed(() => {
  const today = new Date(); today.setHours(0, 0, 0, 0)
  const yesterday = new Date(today); yesterday.setDate(yesterday.getDate() - 1)
  const map = new Map<string, { label: string; sortKey: string; tasks: TaskOut[] }>()

  for (const task of filteredTasks.value) {
    const d = parseDate(task.date); d.setHours(0, 0, 0, 0)
    let label: string, sortKey: string
    if (d.getTime() === today.getTime()) {
      label = '今天'; sortKey = '0'
    } else if (d.getTime() === yesterday.getTime()) {
      label = '昨天'; sortKey = '1'
    } else {
      label = `${d.getMonth() + 1}月${d.getDate()}日`; sortKey = `2_${task.date}`
    }
    if (!map.has(sortKey)) map.set(sortKey, { label, sortKey, tasks: [] })
    map.get(sortKey)!.tasks.push(task)
  }
  return [...map.values()].sort((a, b) => a.sortKey.localeCompare(b.sortKey))
})

async function loadGradedInfo() {
  for (const task of filteredTasks.value) {
    // 加载批改结果
    if (task.status === 'graded' && !(task.id in gradedResult)) {
      try {
        const subs = await listSubmissions(task.id)
        if (subs.length > 0) {
          gradedResult[task.id] = subs[0].is_correct ?? false
          gradedComment[task.id] = subs[0].comment ?? ''
        }
      } catch { /* ignore */ }
    }
    // 加载听写词语
    if (task.has_dictation && !(task.id in dictationWords)) {
      try {
        const items = await getDictationItems(task.id)
        dictationWords[task.id] = items.map(i => i.content)
      } catch {
        dictationWords[task.id] = []
      }
    }
  }
}

function getCardColor(index: number): string {
  const colors = ['card-lilac', 'card-mint', 'card-peach', 'card-green']
  return colors[index % colors.length]
}

async function doGradePass(task: TaskOut) {
  commentModal.task = task
  commentModal.isCorrect = true
  commentModal.text = ''
  commentModal.visible = true
}

async function doGradeFail(task: TaskOut) {
  if (submitting[task.id]) return
  submitting[task.id] = true
  try {
    let subs = await listSubmissions(task.id)
    if (subs.length === 0) {
      try {
        const created = await apiSubmitTask(task.id)
        subs = [created]
      } catch {
        subs = await listSubmissions(task.id)
      }
    }
    if (subs.length === 0) {
      uni.showToast({ title: '找不到提交记录', icon: 'none' })
      return
    }
    await gradeSubmission(subs[0].id, false, '还需要复习哦')
    gradedResult[task.id] = false
    gradedComment[task.id] = '还需要复习哦'
    loadTasksForFilter()
    uni.showToast({ title: '已标记需要复习', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message || '提交失败', icon: 'none' })
  } finally {
    delete submitting[task.id]
  }
}

async function submitGrade(comment: string) {
  const task = commentModal.task!
  if (submitting[task.id]) return
  submitting[task.id] = true
  try {
    let subs = await listSubmissions(task.id)
    if (subs.length === 0) {
      try {
        const created = await apiSubmitTask(task.id)
        subs = [created]
      } catch {
        subs = await listSubmissions(task.id)
      }
    }
    if (subs.length === 0) {
      uni.showToast({ title: '找不到提交记录', icon: 'none' })
      return
    }
    await gradeSubmission(subs[0].id, commentModal.isCorrect, comment || undefined)
    gradedResult[task.id] = commentModal.isCorrect
    gradedComment[task.id] = comment
    loadTasksForFilter()
    uni.showToast({ title: commentModal.isCorrect ? '已标记合格' : '已标记不合格', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message || '提交失败', icon: 'none' })
  } finally {
    delete submitting[task.id]
  }
}

function closeCommentModal() {
  commentModal.visible = false
}

function skipModal() {
  commentModal.visible = false
}

function confirmModal() {
  commentModal.visible = false
  submitGrade(commentModal.text.trim())
}

onMounted(async () => {
  const info = uni.getSystemInfoSync()
  statusBarHeight.value = info.statusBarHeight || 0
  await authStore.init()
  loadFamilyCode()
})

onShow(() => {
  loadTasksForFilter()
})
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

.page {
  min-height: 100vh;
  background: $color-organic-bg;
  font-family: 'Inter', sans-serif;
  position: relative;
}

// ─── Organic Background ───
.organic-bg {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;

  .blob {
    position: absolute;
    filter: blur(60px);
    opacity: 0.5;
  }

  .blob-1 {
    top: -10%; left: -10%;
    width: 50vw; height: 50vw;
    background: $color-soft-lilac;
    border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%;
  }

  .blob-2 {
    bottom: -10%; right: -10%;
    width: 60vw; height: 60vw;
    background: $color-pale-peach;
    border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
  }

  .blob-3 {
    top: 40%; left: 60%;
    width: 40vw; height: 40vw;
    background: $color-mint-green-bright;
    border-radius: 50%;
  }
}

// ─── Glass Card Shared ───
.glass-card {
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 2px solid rgba(255, 255, 255, 0.8);
}

// ─── Main Scroll ───
.main {
  position: relative;
  z-index: 1;
  padding: 0 24px;
  box-sizing: border-box;
  height: 100vh;
}

// ─── Header Section ───
.header-section {
  margin-bottom: 16px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-title {
  font-family: 'Inter', sans-serif;
  font-size: 24px;
  font-weight: 800;
  color: $color-organic-on-surface;
  line-height: 32px;
}

// ─── Filter Dropdown ───
.filter-wrapper {
  position: relative;
}

.filter-pill {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 20px;
  border-radius: 9999px;
  background: $color-organic-surface-container-lowest;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: all 0.15s;
  &:active { transform: scale(0.97); }
}

.filter-pill-text {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 700;
  color: $color-organic-on-surface;
  line-height: 16px;
}

.filter-pill-arrow {
  font-size: 16px !important;
  color: $color-organic-on-surface-variant;
}

.filter-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 100px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  padding: 4px;
  z-index: 100;
}

.filter-option {
  padding: 8px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.15s;
  &:active { background: rgba($color-mint-green-bright, 0.3); }
}

.filter-option-active {
  background: rgba($color-mint-green-bright, 0.4);
}

.filter-option-text {
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 500;
  color: $color-organic-on-surface;
  line-height: 18px;
}

// ─── Statistics Card ───
.stats-card {
  display: flex;
  background: $color-organic-surface-container-lowest;
  border-radius: 32px;
  padding: 16px;
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.06);
  gap: 0;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 48px;
  padding: 8px 0;
}

.stat-label {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 700;
  color: $color-organic-text-secondary;
  line-height: 16px;
  margin-bottom: 4px;
}

.stat-value {
  font-family: 'Inter', sans-serif;
  font-size: 36px;
  font-weight: 900;
  letter-spacing: -0.02em;
  line-height: 44px;
}

.stat-total { color: $color-organic-primary; }
.stat-pass { color: $color-organic-secondary; }
.stat-pending { color: $color-error; }

.stat-divider {
  width: 1px;
  align-self: stretch;
  background: rgba($color-organic-outline-variant, 0.3);
  margin: 0;
}

// ─── Empty State ───
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: 16px;
}

.empty-blob {
  width: 80px; height: 80px;
  border-radius: 50% 50% 40% 60% / 60% 40% 60% 40%;
  background: $color-soft-lilac;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  font-size: 40px;
  color: rgba($color-organic-on-surface, 0.4);
}

.empty-text {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: $color-organic-text-secondary;
}

// ─── Date Group ───
.date-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.date-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 4px;
}

.date-pill {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 9999px;
  background: $color-organic-surface-container-lowest;
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.06);
  white-space: nowrap;
  width: auto;
  box-sizing: border-box;
}

.date-pill-icon {
  font-size: 14px !important;
  color: $color-organic-secondary;
  font-family: 'Material Symbols Outlined';
  font-weight: normal; font-style: normal;
  line-height: 1;
  letter-spacing: normal; text-transform: none;
  white-space: nowrap; word-wrap: normal; direction: ltr;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.date-pill-text {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 700;
  color: $color-organic-on-surface;
  line-height: 14px;
}

.date-line {
  flex: 1;
  height: 0;
  border-top: 2px dashed rgba($color-organic-outline-variant, 0.5);
}

// ─── Task Card ───
.task-card {
  border-radius: 32px;
  padding: 24px;
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.06);
  transition: transform 0.3s;
}

.stagger-left {
  transform: translateX(-8px) rotate(-1deg);
}

.stagger-right {
  transform: translateX(8px) rotate(1deg);
}

// Card color variants
.card-lilac { background: rgba($color-soft-lilac, 0.6); }
.card-mint { background: rgba($color-mint-green, 0.6); }
.card-peach { background: rgba($color-pale-peach, 0.6); }
.card-green { background: rgba($color-mint-green-bright, 0.6); }

// ─── Card Top ───
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.card-title {
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: $color-organic-on-surface;
  line-height: 24px;
  flex: 1;
  margin-right: 8px;
}

// ─── Status Badge ───
.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 9999px;
  background: $color-organic-surface-container-lowest;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  white-space: nowrap;
  flex-shrink: 0;
}

.badge-icon {
  font-size: 16px;
  color: $color-organic-secondary;
}

.badge-text {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 700;
  color: $color-organic-secondary;
}

.badge-fail {
  .badge-icon { color: $color-error; }
  .badge-text { color: $color-error; background: rgba($color-error, 0.08); padding: 1px 4px; border-radius: 4px; }
}

.badge-fail.status-badge {
  background: rgba($color-error, 0.1);
  border-color: rgba($color-error, 0.2);
}

// ─── Card Description ───
.card-desc {
  margin-bottom: 20px;
}

.desc-text {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  color: rgba($color-organic-on-surface, 0.9);
}

// ─── Dictation Words ───
.dictation-section {
  margin-bottom: 16px;
}

.dictation-words {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.word-pill {
  padding: 6px 12px;
  border-radius: 9999px;
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 700;
  color: $color-organic-on-surface;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

// ─── Comment Section ───
.comment-section {
  margin-top: 16px;
}

.comment-bubble {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 16px;
  padding: 12px;
  border-left: 3px solid $color-organic-secondary;
}

.comment-top {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 4px;
}

.comment-icon {
  font-size: 14px;
  color: $color-organic-secondary;
}

.comment-label {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 600;
  color: $color-organic-secondary;
}

.comment-text {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: $color-organic-on-surface;
  line-height: 20px;
}

// ─── Grade Row ───
.grade-row {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 2px dashed rgba(255, 255, 255, 0.5);
}

.grade-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 9999px;
  border: 2px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.15s;
  &:active { transform: scale(0.95); opacity: 0.9; }
}

.grade-btn-icon {
  font-size: 16px;
}

.grade-btn-text {
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  font-weight: 700;
}

.btn-fail {
  background: $color-error;
  .grade-btn-text, .grade-btn-icon { color: #fff; }
}

.btn-pass {
  background: $color-mint-green-dim;
  .grade-btn-text, .grade-btn-icon { color: $color-organic-on-secondary-container; }
}

// ─── Waiting Row ───
.waiting-row {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 2px dashed rgba(255, 255, 255, 0.5);
  text-align: right;
}

.waiting-text {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: $color-organic-text-secondary;
}

// ─── Bottom Spacer ───
.bottom-spacer {
  height: 120px;
}

// ═══════════════════════════════════════════════════
//  Modals
// ═══════════════════════════════════════════════════

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(28, 27, 28, 0.3);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 24px;
}

// ─── Family Code Modal ───
.family-modal {
  background: $color-organic-surface-container-lowest;
  width: 100%;
  max-width: 360px;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.08);
  padding: 32px 24px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.family-icon-wrap {
  width: 64px; height: 64px;
  border-radius: 50% 50% 40% 60% / 60% 40% 60% 40%;
  background: $color-soft-lilac;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.family-icon {
  font-size: 32px;
  color: rgba($color-organic-on-surface, 0.6);
}

.family-modal-title {
  font-family: 'Inter', sans-serif;
  font-size: 24px;
  font-weight: 600;
  color: $color-organic-on-surface;
  margin-bottom: 16px;
}

.family-code {
  font-family: 'Inter', sans-serif;
  font-size: 40px;
  font-weight: 700;
  color: $color-organic-secondary;
  letter-spacing: 8px;
  margin-bottom: 8px;
}

.family-hint {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: $color-organic-text-secondary;
  margin-bottom: 24px;
}

.family-close-btn {
  width: 100%;
  padding: 14px 0;
  border-radius: 16px;
  background: $color-organic-primary;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.15s;
  &:active { transform: scale(0.97); }
}

.family-close-text {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
  color: #fff;
}

// ─── Comment Modal ───
.comment-modal {
  background: $color-organic-surface-container-lowest;
  border-radius: 24px;
  padding: 20px;
  width: 320px;
  max-width: 90vw;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.08);
}

.cm-title {
  font-family: 'Inter', sans-serif;
  font-size: 18px;
  font-weight: 600;
  color: $color-organic-on-surface;
  text-align: center;
}

.cm-textarea {
  background: $color-organic-surface-container-low;
  border: 2px solid $color-organic-outline-variant;
  border-radius: 16px;
  padding: 12px;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  color: $color-organic-on-surface;
  height: 80px;
  width: 100%;
  box-sizing: border-box;
}

.cm-btns {
  display: flex;
  gap: 12px;
}

.cm-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 14px 0;
  border-radius: 16px;
  transition: all 0.15s;
  &:active { transform: scale(0.97); }
}

.cm-skip {
  background: $color-organic-surface-container;
}

.cm-confirm {
  background: $color-dark-green;
  box-shadow: 0 4px 12px rgba(29, 59, 22, 0.2);
}

.cm-btn-text {
  font-family: 'Inter', sans-serif;
  font-size: 14px;
  font-weight: 500;
}

.cm-skip-text { color: $color-organic-on-surface; }
.cm-confirm-text { color: #fff; }
</style>
