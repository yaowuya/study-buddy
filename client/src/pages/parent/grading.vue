<template>
  <view class="page">
    <!-- AppBar -->
    <view class="appbar" :style="{ paddingTop: Math.max(statusBarHeight, 12) + 'px' }">
      <view class="appbar-left">
        <view class="avatar-circle">
          <text class="material-symbols-outlined">person</text>
        </view>
        <text class="appbar-title">家长助手</text>
      </view>
    </view>

    <scroll-view scroll-y class="main" :style="{ paddingTop: (appbarHeight + 8) + 'px' }">
      <view v-if="dateGroups.length === 0" class="empty">
        <text class="material-symbols-outlined empty-icon">history</text>
        <text class="empty-text">暂无历史记录</text>
      </view>

      <view v-for="group in dateGroups" :key="group.label" class="date-group">
        <view class="date-header">
          <text class="date-label">{{ group.label }}</text>
          <view class="date-line"></view>
        </view>

        <view v-for="task in group.tasks" :key="task.id" class="task-card">
          <view :class="['accent-bar', `accent-${task.subject || 'default'}`]"></view>

          <view class="card-body">
            <view class="card-top">
              <view class="chip-row">
                <view :class="['subject-chip', `chip-${task.subject || 'default'}`]">
                  <text class="chip-text">{{ task.subject || '其他' }}</text>
                </view>
                <text v-if="task.updated_at" class="finish-time">{{ formatTime(task.updated_at) }} 完成</text>
              </view>
              <text class="task-title">{{ task.title }}</text>
            </view>

            <!-- 待评价 -->
            <view v-if="task.status === 'submitted'" class="card-bottom">
              <text class="pending-hint">请评价</text>
              <view class="grade-btns">
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

            <!-- 已评价 -->
            <view v-else-if="task.status === 'graded'" class="card-bottom">
              <view class="rated-row" :class="gradedResult[task.id] ? 'rated-pass' : 'rated-fail'">
                <text class="material-symbols-outlined rated-icon">
                  {{ gradedResult[task.id] ? 'check_circle' : 'cancel' }}
                </text>
                <text class="rated-text">{{ gradedResult[task.id] ? '合格' : '不合格' }}</text>
              </view>
              <text v-if="gradedComment[task.id]" class="rated-comment">{{ gradedComment[task.id] }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="bottom-spacer"></view>
    </scroll-view>

    <!-- 评语弹窗 -->
    <view v-if="commentModal.visible" class="modal-mask" @tap="cancelModal">
      <view class="modal-box" @tap.stop>
        <text class="modal-title">添加评语（可选）</text>
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
        <text class="material-symbols-outlined nav-icon">auto_stories</text>
        <text class="nav-label">作业</text>
      </view>
      <view class="nav-item" @tap="goCreate">
        <text class="material-symbols-outlined nav-icon">add_circle</text>
        <text class="nav-label">布置</text>
      </view>
      <view class="nav-item nav-item-active">
        <text class="material-symbols-outlined nav-icon nav-icon-fill">history</text>
        <text class="nav-label">历史</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useTasksStore } from '@/stores/tasks'
import { gradeSubmission, listSubmissions, submitTask as apiSubmitTask } from '@/api/submissions'
import type { TaskOut } from '@/api/tasks'

const tasksStore = useTasksStore()
const statusBarHeight = ref(0)
const safeAreaBottom = ref(0)
const appbarHeight = ref(68)

// taskId -> is_correct
const gradedResult = reactive<Record<string, boolean>>({})
// taskId -> comment
const gradedComment = reactive<Record<string, string>>({})
// 提交中的 taskId 集合，防止重复点击
const submitting = reactive<Record<string, boolean>>({})

// 评语弹窗状态
const commentModal = reactive({
  visible: false,
  task: null as TaskOut | null,
  isCorrect: false,
  text: '',
})

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
  for (const task of allTasks.value.filter(t => t.status === 'graded')) {
    if (task.id in gradedResult) continue
    try {
      const subs = await listSubmissions(task.id)
      if (subs.length > 0) {
        gradedResult[task.id] = subs[0].is_correct ?? false
        gradedComment[task.id] = subs[0].comment ?? ''
      }
    } catch { /* ignore */ }
  }
}

async function doGrade(task: TaskOut, isCorrect: boolean) {
  // 直接弹框，不做任何网络请求
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
    // 查 submission，没有就创建（忽略创建失败，再查一次）
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
    // 调批改接口
    await gradeSubmission(subs[0].id, commentModal.isCorrect, comment || undefined)
    gradedResult[task.id] = commentModal.isCorrect
    gradedComment[task.id] = comment
    await tasksStore.fetchTodayTasks()
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

function goDashboard() { uni.redirectTo({ url: '/pages/parent/dashboard' }) }
function goCreate() { uni.redirectTo({ url: '/pages/parent/task-create' }) }

onMounted(() => {
  const info = uni.getSystemInfoSync()
  statusBarHeight.value = info.statusBarHeight || 0
  safeAreaBottom.value = info.safeAreaInsets?.bottom || 0
  uni.createSelectorQuery().select('.appbar').boundingClientRect((rect: any) => {
    if (rect && rect.height) appbarHeight.value = rect.height
  }).exec()
})

onShow(() => {
  tasksStore.fetchTodayTasks().then(loadGradedInfo)
})
</script>

<style lang="scss" scoped>
@use '@/static/styles/variables.scss' as *;

.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-weight: normal; font-style: normal; font-size: 24px; line-height: 1;
  letter-spacing: normal; text-transform: none; display: inline-block;
  white-space: nowrap; word-wrap: normal; direction: ltr;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.page { min-height: 100vh; background: $color-surface; font-family: $font-family-body; }

.appbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: #fff; border-bottom: 2px solid #f1f5f9;
  display: flex; align-items: center; justify-content: space-between;
  padding-left: $spacing-margin; padding-right: $spacing-margin;
  padding-bottom: 12px; min-height: 64px; box-sizing: border-box;
}
.appbar-left { display: flex; align-items: center; gap: $spacing-sm; }
.avatar-circle {
  width: 40px; height: 40px; border-radius: $radius-full;
  background: $color-primary-fixed; display: flex; align-items: center; justify-content: center;
  color: $color-primary;
}
.appbar-title { font-family: $font-family; font-size: 18px; font-weight: 800; color: #2563eb; }
.appbar-icon-btn {
  width: 40px; height: 40px; border-radius: $radius-full;
  display: flex; align-items: center; justify-content: center; color: #3b82f6;
}

.main { flex: 1; padding: 0 $spacing-margin; box-sizing: border-box; width: 100%; }

.date-group { margin-bottom: $spacing-lg; }
.date-header { display: flex; align-items: center; gap: $spacing-sm; margin-bottom: $spacing-md; }
.date-label { font-family: $font-family; font-size: $font-headline-lg; font-weight: 600; color: $color-on-surface; white-space: nowrap; }
.date-line { flex: 1; height: 1px; background: rgba($color-outline-variant, 0.4); border-radius: 999px; }

.task-card {
  background: $color-surface-container-lowest; border-radius: 24px;
  border: 1px solid $color-surface-container-highest;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  margin-bottom: $spacing-md; display: flex; overflow: hidden;
}
.accent-bar { width: 8px; flex-shrink: 0; }
.accent-语文 { background: #4fdbcc; }
.accent-数学 { background: $color-primary-fixed; }
.accent-英语 { background: #edc157; }
.accent-科学 { background: $color-outline; }
.accent-default { background: $color-outline-variant; }

.card-body { flex: 1; padding: $spacing-md; display: flex; flex-direction: column; gap: $spacing-sm; }
.card-top { display: flex; flex-direction: column; gap: $spacing-xs; }
.chip-row { display: flex; align-items: center; gap: $spacing-xs; }
.subject-chip {
  padding: 2px 12px; border-radius: 999px;
  font-family: $font-family; font-size: $font-label-sm; font-weight: 600; white-space: nowrap;
}
.chip-语文 { background: $color-tertiary-fixed; color: #00201d; }
.chip-数学 { background: $color-primary-fixed; color: #001a41; }
.chip-英语 { background: #ffdf9b; color: #251a00; }
.chip-科学 { background: $color-surface-container-highest; color: $color-on-surface-variant; }
.chip-default { background: $color-surface-container-highest; color: $color-on-surface-variant; }
.chip-text { color: inherit; }
.finish-time { font-family: $font-family; font-size: $font-label-sm; color: $color-outline; }
.task-title { font-family: $font-family-body; font-size: $font-body-lg; font-weight: 500; color: $color-on-surface; display: block; }

.card-bottom {
  padding-top: $spacing-sm; border-top: 1px solid $color-surface-container-highest;
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: $spacing-xs;
}
.pending-hint { font-family: $font-family; font-size: $font-label-md; color: $color-primary; }

// 评价按钮
.grade-btns { display: flex; gap: $spacing-sm; }
.grade-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 7px 16px; border-radius: $radius-xl;
  border-bottom: 3px solid transparent;
  &:active { border-bottom-width: 0; transform: translateY(3px); }
}
.btn-pass {
  background: $color-tertiary; border-bottom-color: #004d45;
  .grade-icon, .grade-text { color: #fff; }
}
.btn-fail {
  background: $color-error; border-bottom-color: #7d0f0f;
  .grade-icon, .grade-text { color: #fff; }
}
.grade-icon { font-size: 18px; font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
.grade-text { font-family: $font-family; font-size: $font-label-md; font-weight: 600; }

// 已评价
.rated-row {
  display: flex; align-items: center; gap: 6px;
  padding: 5px 14px; border-radius: $radius-xl;
}
.rated-pass { background: rgba(0,104,95,0.12); }
.rated-fail { background: rgba(186,26,26,0.12); }
.rated-icon {
  font-size: 18px; font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
  .rated-pass & { color: #00685f; }
  .rated-fail & { color: #ba1a1a; }
}
.rated-text {
  font-family: $font-family; font-size: $font-label-md; font-weight: 600;
  .rated-pass & { color: #00685f; }
  .rated-fail & { color: #ba1a1a; }
}
.rated-comment { font-size: $font-label-sm; color: $color-on-surface-variant; font-style: italic; }

// 评语弹窗
.modal-mask {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45); z-index: 200;
  display: flex; align-items: center; justify-content: center;
}
.modal-box {
  background: #fff; border-radius: 24px; padding: $spacing-md;
  width: 320px; max-width: 90vw; display: flex; flex-direction: column; gap: $spacing-md;
}
.modal-title { font-family: $font-family; font-size: $font-body-lg; font-weight: 600; color: $color-on-surface; text-align: center; }
.modal-textarea {
  background: $color-surface-container; border: 2px solid $color-outline-variant;
  border-radius: $radius-xl; padding: $spacing-sm; font-size: $font-body-md;
  color: $color-on-surface; height: 80px; width: 100%; box-sizing: border-box;
}
.modal-btns { display: flex; gap: $spacing-sm; }
.modal-btn {
  flex: 1; display: flex; align-items: center; justify-content: center;
  padding: $spacing-sm; border-radius: $radius-xl;
  border-bottom: 3px solid transparent;
  &:active { border-bottom-width: 0; transform: translateY(3px); }
}
.modal-btn-cancel { background: $color-surface-container; border-bottom-color: $color-outline-variant; }
.modal-btn-cancel .modal-btn-text { color: $color-on-surface-variant; font-family: $font-family; font-size: $font-label-md; font-weight: 600; }
.modal-btn-confirm { background: $color-primary; border-bottom-color: #004494; }
.modal-btn-confirm .modal-btn-text { color: #fff; font-family: $font-family; font-size: $font-label-md; font-weight: 600; }

.empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 80px 0; gap: $spacing-md; }
.empty-icon { font-size: 64px; color: $color-outline-variant; }
.empty-text { font-size: $font-body-md; color: $color-on-surface-variant; }
.bottom-spacer { height: 100px; }

.bottom-nav {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 100;
  background: #fff; border-top: 2px solid #f1f5f9;
  border-top-left-radius: 32px; border-top-right-radius: 32px;
  display: flex; justify-content: space-around; align-items: center;
  height: 80px; padding-top: 12px; padding-left: $spacing-md; padding-right: $spacing-md;
  box-shadow: 0 -4px 10px rgba(58,134,255,0.05);
}
.nav-item {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 6px 20px; color: #94a3b8;
}
.nav-item-active { background: #dbeafe; color: #1d4ed8; border-radius: $radius-2xl; }
.nav-icon { font-size: 24px; }
.nav-icon-fill { font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
.nav-label { font-family: $font-family; font-size: 12px; font-weight: 500; margin-top: 4px; }
</style>
