<template>
  <view class="page">
    <!-- TopAppBar -->
    <view class="appbar" :style="{ paddingTop: Math.max(statusBarHeight, 12) + 'px' }">
      <view class="avatar" @tap="showFamilyCode">
        <text class="material-symbols-outlined">person</text>
      </view>
      <view class="appbar-center">
        <text class="appbar-title">{{ isStudentMode ? '作业伙伴' : '家长助手' }}</text>
        <text v-if="!isStudentMode" class="appbar-code">家庭连接码：{{ familyCode }}</text>
      </view>
      <view class="appbar-icon-btn" @tap="handleLogout">
        <text class="material-symbols-outlined">logout</text>
      </view>
    </view>

    <!-- Main Content -->
    <scroll-view scroll-y class="main" :style="{ paddingTop: (appbarHeight + 8) + 'px' }">
      <!-- Empty State -->
      <view v-if="dateGroups.length === 0" class="empty">
        <text class="material-symbols-outlined empty-icon">history</text>
        <text class="empty-text">暂无历史记录</text>
      </view>

      <!-- Date Groups -->
      <view v-for="group in dateGroups" :key="group.label" class="date-group">
        <view class="date-header">
          <text class="date-label">{{ group.label }}</text>
          <view class="date-line"></view>
        </view>

        <!-- Task Cards -->
        <view v-for="task in group.tasks" :key="task.id" class="task-card">
          <!-- Accent Bar -->
          <view :class="['accent-bar', `accent-${task.subject || 'default'}`]"></view>

          <!-- Card Content -->
          <view class="card-content">
            <!-- Header: Subject + Time + Title -->
            <view class="card-header">
              <view class="chip-row">
                <view :class="['subject-chip', `chip-${task.subject || 'default'}`]">
                  <text class="chip-text">{{ task.subject || '其他' }}</text>
                </view>
                <text v-if="task.updated_at" class="finish-time">{{ formatTime(task.updated_at) }} 完成</text>
              </view>
              <text class="task-title">{{ task.title }}</text>
            </view>

            <!-- Task Description -->
            <view v-if="task.desc" class="task-desc-box">
              <text class="task-desc-text">{{ task.desc }}</text>
            </view>

            <!-- Dictation Words -->
            <view v-if="task.has_dictation && dictationWords[task.id]?.length" class="dictation-section">
              <view class="dictation-header">
                <text class="material-symbols-outlined dictation-icon">record_voice_over</text>
                <text class="dictation-label">听写词语</text>
              </view>
              <view class="dictation-words">
                <text v-for="(word, i) in dictationWords[task.id]" :key="i" class="dictation-word">{{ word }}</text>
              </view>
            </view>

            <!-- Bottom Section -->
            <view class="card-bottom">
              <!-- Parent Comment -->
              <view v-if="task.status === 'graded' && gradedComment[task.id]" class="comment-box">
                <view class="comment-header">
                  <text class="material-symbols-outlined comment-icon">chat_bubble</text>
                  <text class="comment-label">家长评语</text>
                </view>
                <text class="comment-text">{{ gradedComment[task.id] }}</text>
              </view>

              <!-- Status / Action Row -->
              <view class="status-row">
                <!-- Submitted: Pending Grade -->
                <view v-if="task.status === 'submitted'" class="status-pending">
                  <text class="pending-hint">{{ isStudentMode ? '等待家长评价' : '请评价' }}</text>
                  <view v-if="!isStudentMode" class="grade-btns">
                    <view class="grade-btn btn-pass" @tap="doGrade(task, true)">
                      <text class="material-symbols-outlined grade-icon">check_circle</text>
                      <text class="grade-text">合格</text>
                    </view>
                    <view class="grade-btn btn-fail" @tap="doGrade(task, false)">
                      <text class="material-symbols-outlined grade-icon">cancel</text>
                      <text class="grade-text">不合格</text>
                    </view>
                  </view>
                </view>

                <!-- Graded: Result Badge -->
                <view v-else-if="task.status === 'graded'" class="status-graded">
                  <view :class="['result-badge', gradedResult[task.id] ? 'badge-pass' : 'badge-fail']">
                    <text class="material-symbols-outlined badge-icon">
                      {{ gradedResult[task.id] ? 'check_circle' : 'cancel' }}
                    </text>
                    <text class="badge-text">{{ gradedResult[task.id] ? '合格' : '不合格' }}</text>
                  </view>
                </view>
              </view>
            </view>
          </view>
        </view>
      </view>

      <view class="bottom-spacer"></view>
    </scroll-view>

    <!-- Family Code Modal -->
    <view v-if="showCode" class="modal-overlay" @tap="showCode = false">
      <view class="modal-content" @tap.stop>
        <text class="modal-title">家庭连接码</text>
        <text class="modal-code">{{ familyCode }}</text>
        <text class="modal-hint">让学生输入此码完成绑定</text>
      </view>
    </view>

    <!-- Comment Modal -->
    <view v-if="commentModal.visible" class="modal-overlay" @tap="cancelModal">
      <view class="modal-box" @tap.stop>
        <text class="modal-box-title">添加评语（可选）</text>
        <textarea
          v-model="commentModal.text"
          class="modal-textarea"
          placeholder="写下你的评语…"
          maxlength="100"
        />
        <view class="modal-btns">
          <view class="modal-btn modal-btn-cancel" @tap="cancelModal">
            <text class="modal-btn-text">跳过</text>
          </view>
          <view class="modal-btn modal-btn-confirm" @tap="confirmModal">
            <text class="modal-btn-text">确认</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Bottom Nav -->
    <view class="bottom-nav" :style="{ paddingBottom: safeAreaBottom + 'px' }">
      <view class="nav-item" @tap="goDashboard">
        <text class="material-symbols-outlined nav-icon">menu_book</text>
        <text class="nav-label">作业</text>
      </view>
      <view v-if="!isStudentMode" class="nav-item" @tap="goCreate">
        <text class="material-symbols-outlined nav-icon">add_circle</text>
        <text class="nav-label">布置</text>
      </view>
      <view class="nav-item nav-item-active">
        <text class="material-symbols-outlined nav-icon">history</text>
        <text class="nav-label">历史</text>
      </view>
    </view>
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

const authStore = useAuthStore()
const tasksStore = useTasksStore()
const showCode = ref(false)
const familyCode = ref('加载中')

const statusBarHeight = ref(0)
const safeAreaBottom = ref(0)
const appbarHeight = ref(88) // 增加默认值

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

const allTasks = computed(() =>
  (Array.isArray(tasksStore.tasks) ? tasksStore.tasks : [])
    .filter(t => t.status === 'submitted' || t.status === 'graded')
)

const dateGroups = computed(() => {
  const today = new Date(); today.setHours(0, 0, 0, 0)
  const yesterday = new Date(today); yesterday.setDate(yesterday.getDate() - 1)
  const map = new Map<string, { label: string; sortKey: string; tasks: TaskOut[] }>()

  for (const task of allTasks.value) {
    const d = new Date(task.date); d.setHours(0, 0, 0, 0)
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

function formatTime(isoStr: string) {
  try {
    const d = new Date(isoStr)
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  } catch { return '' }
}

async function loadGradedInfo() {
  for (const task of allTasks.value) {
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

async function doGrade(task: TaskOut, isCorrect: boolean) {
  commentModal.task = task
  commentModal.isCorrect = isCorrect
  commentModal.text = ''
  commentModal.visible = true
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
    await tasksStore.fetchAllTasks()
    uni.showToast({ title: commentModal.isCorrect ? '已标记合格' : '已标记不合格', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message || '提交失败', icon: 'none' })
  } finally {
    delete submitting[task.id]
  }
}

function cancelModal() {
  commentModal.visible = false
  submitGrade('')
}

function confirmModal() {
  commentModal.visible = false
  submitGrade(commentModal.text.trim())
}

function showFamilyCode() {
  if (!isStudentMode.value) {
    showCode.value = true
  }
}

function goDashboard() {
  if (isStudentMode.value) {
    uni.redirectTo({ url: '/pages/student/home' })
  } else {
    uni.redirectTo({ url: '/pages/parent/dashboard' })
  }
}

function goCreate() {
  uni.redirectTo({ url: '/pages/parent/task-create' })
}

onMounted(() => {
  const info = uni.getSystemInfoSync()
  statusBarHeight.value = info.statusBarHeight || 0
  safeAreaBottom.value = info.safeAreaInsets?.bottom || 0
  // AppBar 高度 = statusBarHeight + 顶部padding + 内容高度(56) + 底部padding
  appbarHeight.value = Math.max(statusBarHeight.value, 12) + 56 + 12
  loadFamilyCode()
})

onShow(() => {
  tasksStore.fetchAllTasks().then(loadGradedInfo)
})
</script>

<style lang="scss" scoped>
@use '@/static/styles/variables.scss' as *;

// 补充缺失的变量
$color-on-primary-fixed: #001a41;
$color-on-tertiary-fixed: #00201d;

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
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.page {
  min-height: 100vh;
  background: $color-surface;
  font-family: $font-family-body;
}

// AppBar
.appbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: #fff;
  border-bottom: 1px solid $color-surface-container;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 $spacing-margin;
  padding-bottom: 12px;
  min-height: 64px;
  box-sizing: border-box;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: $radius-full;
  background: $color-primary-fixed;
  display: flex;
  align-items: center;
  justify-content: center;
  color: $color-on-primary-fixed;
  border: 2px solid $color-surface-container-highest;
}

.appbar-center {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.appbar-title {
  font-family: $font-family;
  font-size: 20px;
  font-weight: 800;
  color: $color-primary;
}

.appbar-code {
  font-family: $font-family;
  font-size: $font-label-sm;
  font-weight: 500;
  color: $color-on-surface-variant;
  margin-top: 2px;
}

.appbar-icon-btn {
  width: 40px;
  height: 40px;
  border-radius: $radius-full;
  display: flex;
  align-items: center;
  justify-content: center;
  color: $color-on-surface-variant;
}

// Main
.main {
  padding: 0 $spacing-margin;
  box-sizing: border-box;
}

// Date Group
.date-group {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  margin-bottom: $spacing-sm;
}

.date-header {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.date-label {
  font-family: $font-family;
  font-size: $font-headline-lg;
  font-weight: 600;
  color: $color-on-surface;
  white-space: nowrap;
}

.date-line {
  flex: 1;
  height: 1px;
  background: rgba($color-outline-variant, 0.3);
  border-radius: $radius-full;
}

// Task Card
.task-card {
  background: $color-surface-container-lowest;
  border-radius: $radius-lg;
  padding: $spacing-md;
  border: 1px solid $color-surface-container;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.accent-bar {
  position: absolute;
  top: 0;
  left: 0;
  width: 6px;
  height: 100%;
  border-radius: $radius-lg 0 0 $radius-lg;
}

.accent-语文 { background: $color-tertiary-fixed-dim; }
.accent-数学 { background: $color-primary-fixed-dim; }
.accent-英语 { background: $color-secondary-fixed-dim; }
.accent-科学 { background: $color-outline; }
.accent-default { background: $color-outline-variant; }

.card-content {
  margin-left: $spacing-sm;
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

// Header
.card-header {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.chip-row {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

.subject-chip {
  padding: 2px 12px;
  border-radius: $radius-full;
  font-family: $font-family;
  font-size: $font-label-sm;
  font-weight: 600;
  white-space: nowrap;
}

.chip-语文 { background: $color-tertiary-fixed; color: $color-on-tertiary-fixed; }
.chip-数学 { background: $color-primary-fixed; color: $color-on-primary-fixed; }
.chip-英语 { background: $color-secondary-fixed; color: #251a00; }
.chip-科学 { background: $color-surface-container-highest; color: $color-on-surface-variant; }
.chip-default { background: $color-surface-container-highest; color: $color-on-surface-variant; }

.finish-time {
  font-family: $font-family;
  font-size: $font-label-sm;
  color: $color-outline;
}

.task-title {
  font-family: $font-family-body;
  font-size: $font-body-lg;
  font-weight: 500;
  color: $color-on-surface;
}

// Task Description
.task-desc-box {
  margin-top: $spacing-xs;
  background: $color-surface-container-low;
  border-radius: $radius-lg;
  padding: $spacing-sm;
}

.task-desc-text {
  font-size: $font-body-md;
  color: $color-on-surface-variant;
  line-height: 1.5;
}

// Dictation Section
.dictation-section {
  margin-top: $spacing-xs;
  background: $color-surface-container-low;
  border-radius: $radius-lg;
  padding: $spacing-sm;
}

.dictation-header {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: $spacing-xs;
}

.dictation-icon {
  font-size: 16px;
  color: $color-tertiary;
}

.dictation-label {
  font-family: $font-family;
  font-size: $font-label-sm;
  font-weight: 600;
  color: $color-tertiary;
}

.dictation-words {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-xs;
}

.dictation-word {
  background: #fff;
  padding: 4px 12px;
  border-radius: $radius-md;
  font-family: $font-family;
  font-size: $font-body-md;
  color: $color-on-surface;
  border: 1px solid $color-surface-container-highest;
}

// Bottom Section
.card-bottom {
  margin-top: $spacing-xs;
  padding-top: $spacing-sm;
  border-top: 1px solid $color-surface-container;
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

// Comment Box
.comment-box {
  background: $color-surface-container-low;
  border-radius: $radius-lg;
  padding: $spacing-sm;
  border-left: 2px solid $color-primary;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 4px;
}

.comment-icon {
  font-size: 14px;
  color: $color-primary;
}

.comment-label {
  font-family: $font-family;
  font-size: $font-label-sm;
  font-weight: 600;
  color: $color-primary;
}

.comment-text {
  font-size: $font-body-md;
  color: $color-on-surface;
  line-height: 1.5;
}

// Status Row
.status-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-pending {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.pending-hint {
  font-family: $font-family;
  font-size: $font-label-md;
  color: $color-primary;
}

.grade-btns {
  display: flex;
  gap: $spacing-sm;
}

.grade-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border-radius: $radius-full;
  border-bottom: 3px solid transparent;
  &:active {
    border-bottom-width: 0;
    transform: translateY(3px);
  }
}

.btn-pass {
  background: $color-tertiary;
  border-bottom-color: #004d45;
}

.btn-fail {
  background: $color-error;
  border-bottom-color: #7d0f0f;
}

.grade-icon {
  font-size: 16px;
  color: #fff;
}

.grade-text {
  font-family: $font-family;
  font-size: $font-label-md;
  font-weight: 600;
  color: #fff;
}

// Result Badge
.result-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: $radius-full;
}

.badge-pass {
  background: rgba($color-tertiary-container, 0.2);
}

.badge-fail {
  background: rgba($color-error, 0.12);
}

.badge-icon {
  font-size: 16px;
  .badge-pass & { color: $color-tertiary; }
  .badge-fail & { color: $color-error; }
}

.badge-text {
  font-family: $font-family;
  font-size: $font-label-md;
  font-weight: 600;
  .badge-pass & { color: $color-tertiary; }
  .badge-fail & { color: $color-error; }
}

// Empty State
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: $spacing-md;
}

.empty-icon {
  font-size: 64px;
  color: $color-outline-variant;
}

.empty-text {
  font-size: $font-body-md;
  color: $color-on-surface-variant;
}

.bottom-spacer {
  height: 100px;
}

// Modals
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal-content {
  background: #fff;
  padding: $spacing-lg;
  border-radius: $radius-2xl;
  text-align: center;
  width: 300px;
}

.modal-title {
  font-size: $font-card-title;
  font-weight: 600;
  display: block;
  margin-bottom: $spacing-md;
}

.modal-code {
  font-size: 40px;
  font-weight: 700;
  color: $color-primary;
  letter-spacing: 8px;
  display: block;
  margin-bottom: $spacing-sm;
}

.modal-hint {
  font-size: $font-body-md;
  color: $color-on-surface-variant;
}

.modal-box {
  background: #fff;
  border-radius: $radius-2xl;
  padding: $spacing-md;
  width: 320px;
  max-width: 90vw;
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.modal-box-title {
  font-family: $font-family;
  font-size: $font-body-lg;
  font-weight: 600;
  color: $color-on-surface;
  text-align: center;
}

.modal-textarea {
  background: $color-surface-container;
  border: 2px solid $color-outline-variant;
  border-radius: $radius-xl;
  padding: $spacing-sm;
  font-size: $font-body-md;
  color: $color-on-surface;
  height: 80px;
  width: 100%;
  box-sizing: border-box;
}

.modal-btns {
  display: flex;
  gap: $spacing-sm;
}

.modal-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $spacing-sm;
  border-radius: $radius-xl;
  border-bottom: 3px solid transparent;
  &:active {
    border-bottom-width: 0;
    transform: translateY(3px);
  }
}

.modal-btn-cancel {
  background: $color-surface-container;
  border-bottom-color: $color-outline-variant;
}

.modal-btn-confirm {
  background: $color-primary;
  border-bottom-color: #004494;
}

.modal-btn-text {
  font-family: $font-family;
  font-size: $font-label-md;
  font-weight: 600;
  .modal-btn-cancel & { color: $color-on-surface-variant; }
  .modal-btn-confirm & { color: #fff; }
}

// Bottom Nav
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: #fff;
  border-top: 1px solid $color-surface-container;
  border-top-left-radius: $radius-2xl;
  border-top-right-radius: $radius-2xl;
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding-top: 12px;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.05);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 6px 24px;
  color: $color-outline;
}

.nav-item-active {
  background: rgba($color-primary-container, 0.2);
  color: $color-primary;
  border-radius: $radius-full;
}

.nav-icon {
  font-size: 24px;
  margin-bottom: 2px;
}

.nav-label {
  font-family: $font-family;
  font-size: 10px;
  font-weight: 500;
}
</style>
