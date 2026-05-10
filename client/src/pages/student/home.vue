<template>
  <view class="student-home">
    <text class="greeting">今日任务</text>

    <view v-if="tasks.length === 0" class="empty">
      <text class="empty-text">今天没有任务，休息一下吧！</text>
    </view>

    <view v-else class="task-list">
      <view v-for="task in tasks" :key="task.id" :class="['task-card', `card-${task.type}`]" @tap="handleTaskTap(task)">
        <view class="card-top">
          <text :class="['type-pill', `pill-${task.type}`]">{{ task.type === 'school' ? '学校' : '家庭' }}</text>
          <text :class="['status-text', `st-${task.status}`]">{{ statusLabel(task.status) }}</text>
        </view>
        <text class="card-title">{{ task.title }}</text>
        <text v-if="task.desc" class="card-desc">{{ task.desc }}</text>
        <view v-if="task.duration" class="card-meta">
          <text class="duration">{{ task.duration }}分钟</text>
        </view>

        <view class="card-action">
          <button v-if="task.status === 'pending'" class="action-btn btn-start" @tap.stop="startTask(task)">开始</button>
          <button v-if="task.status === 'in_progress'" class="action-btn btn-done" @tap.stop="doneTask(task)">完成</button>
          <text v-if="task.status === 'submitted'" class="action-wait">等待批改</text>
          <text v-if="task.status === 'graded'" class="action-done">已完成</text>
        </view>
      </view>
    </view>

    <view v-if="showCelebration" class="celebration" @tap="showCelebration = false">
      <text class="celebration-emoji">&#127881;</text>
      <text class="celebration-text">太棒了！全部完成！</text>
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
const showCelebration = ref(false)

const tasks = computed(() => tasksStore.tasks)

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '未开始', in_progress: '进行中', submitted: '待批改', graded: '已批改'
  }
  return map[status] || status
}

function handleTaskTap(task: TaskOut) {
  uni.navigateTo({ url: `/pages/student/dictation?taskId=${task.id}` })
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

onMounted(() => {
  tasksStore.loadCached()
})

onShow(() => {
  tasksStore.fetchTodayTasks()
  syncStore.start()
})
</script>

<style lang="scss" scoped>
@import '@/static/styles/variables.scss';

.student-home { padding: $spacing-md; min-height: 100vh; }
.greeting { font-size: $font-hero; font-weight: 700; color: $color-primary-light; display: block; margin-bottom: $spacing-md; }

.task-list { display: flex; flex-direction: column; gap: $spacing-md; }

.task-card {
  padding: $card-padding; background: #fff; border-radius: $radius-xl;
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
.card-school { border-left: 6px solid $color-primary; }
.card-home { border-left: 6px solid #8B5CF6; }

.card-top { display: flex; justify-content: space-between; margin-bottom: 8px; }
.type-pill {
  font-size: $font-label; font-weight: 600; padding: 4px 12px; border-radius: $radius-full;
}
.pill-school { background: rgba($color-primary, 0.1); color: $color-primary; }
.pill-home { background: rgba(#8B5CF6, 0.1); color: #8B5CF6; }
.status-text { font-size: $font-label; font-weight: 500; }
.st-pending { color: $color-on-surface-variant; }
.st-in_progress { color: #F59E0B; }
.st-submitted { color: $color-primary; }
.st-graded { color: $color-tertiary; }

.card-title { font-size: $font-card-title; font-weight: 600; display: block; }
.card-desc { font-size: $font-body-md; color: $color-on-surface-variant; margin-top: 4px; display: block; }
.card-meta { margin-top: 8px; }
.duration { font-size: $font-label; color: $color-outline; }

.card-action { margin-top: $spacing-sm; }
.action-btn {
  min-height: $touch-min; border-radius: $radius-md; font-size: $font-body-md; font-weight: 600; border: none;
}
.btn-start { background: $color-primary; color: #fff; }
.btn-done { background: $color-tertiary; color: #fff; }
.action-wait { font-size: $font-body-md; color: $color-primary; }
.action-done { font-size: $font-body-md; color: $color-tertiary; font-weight: 600; }

.celebration {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.7); display: flex; flex-direction: column;
  align-items: center; justify-content: center; z-index: 999;
}
.celebration-emoji { font-size: 80px; }
.celebration-text { font-size: $font-card-title; font-weight: 700; color: #fff; margin-top: $spacing-md; }

.empty { text-align: center; margin-top: 120px; }
.empty-text { font-size: $font-body-lg; color: $color-on-surface-variant; }
</style>
