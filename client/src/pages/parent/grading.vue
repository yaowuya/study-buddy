<template>
  <view class="grading-page">
    <view class="tab-bar">
      <text :class="['tab', filter === 'submitted' ? 'tab-active' : '']" @tap="filter = 'submitted'">待批改</text>
      <text :class="['tab', filter === 'graded' ? 'tab-active' : '']" @tap="filter = 'graded'">已批改</text>
    </view>

    <view v-if="filteredTasks.length === 0" class="empty">
      <text class="empty-text">{{ filter === 'submitted' ? '没有待批改的作业' : '没有已批改的记录' }}</text>
    </view>

    <view v-else class="task-list">
      <view v-for="task in filteredTasks" :key="task.id" class="task-card">
        <text class="task-title">{{ task.title }}</text>
        <text class="task-type">{{ task.type === 'school' ? '学校' : '家庭' }}</text>

        <view v-if="task.status === 'submitted'" class="grade-actions">
          <button class="btn-correct" @tap="handleGrade(task, true)">&#10003; 正确</button>
          <button class="btn-wrong" @tap="handleGrade(task, false)">&#10005; 错误</button>
        </view>

        <view v-if="task.status === 'graded'" class="graded-result">
          <text :class="['result-badge', gradedInfo[task.id]?.isCorrect ? 'badge-correct' : 'badge-wrong']">
            {{ gradedInfo[task.id]?.isCorrect ? '&#10003; 正确' : '&#10005; 错误' }}
          </text>
          <text v-if="gradedInfo[task.id]?.comment" class="comment">{{ gradedInfo[task.id]?.comment }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { useTasksStore } from '@/stores/tasks'
import { gradeSubmission, listSubmissions } from '@/api/submissions'
import type { TaskOut } from '@/api/tasks'

const tasksStore = useTasksStore()
const filter = ref<'submitted' | 'graded'>('submitted')
const gradedInfo = reactive<Record<string, { isCorrect: boolean; comment?: string }>>({})

const filteredTasks = computed(() =>
  tasksStore.tasks.filter(t => t.status === filter.value)
)

async function loadGradedInfo() {
  for (const task of tasksStore.tasks.filter(t => t.status === 'graded')) {
    try {
      const subs = await listSubmissions(task.id)
      if (subs.length > 0) {
        gradedInfo[task.id] = {
          isCorrect: subs[0].is_correct ?? false,
          comment: subs[0].comment ?? undefined,
        }
      }
    } catch { /* ignore */ }
  }
}

async function handleGrade(task: TaskOut, isCorrect: boolean) {
  try {
    const subs = await listSubmissions(task.id)
    if (subs.length === 0) return
    await gradeSubmission(subs[0].id, isCorrect)
    gradedInfo[task.id] = { isCorrect }
    await tasksStore.fetchTodayTasks()
    uni.showToast({ title: isCorrect ? '标记正确' : '标记错误', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

onMounted(() => {
  tasksStore.fetchTodayTasks().then(loadGradedInfo)
})
</script>

<style lang="scss" scoped>
@import '@/static/styles/variables.scss';

.grading-page { padding: $spacing-md; min-height: 100vh; }
.tab-bar { display: flex; gap: $spacing-sm; margin-bottom: $spacing-md; }
.tab {
  padding: 8px $spacing-md; border-radius: $radius-full; font-size: $font-label; font-weight: 500;
  background: rgba($color-primary, 0.06); color: $color-on-surface-variant;
}
.tab-active { background: $color-primary; color: #fff; }

.task-list { display: flex; flex-direction: column; gap: $spacing-sm; }
.task-card {
  padding: $card-padding; background: #fff; border-radius: $radius-xl;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.task-title { font-size: $font-body-lg; font-weight: 600; }
.task-type { font-size: $font-label; color: $color-on-surface-variant; }

.grade-actions { display: flex; gap: $spacing-sm; margin-top: $spacing-sm; }
.btn-correct {
  flex: 1; height: $touch-min; background: $color-tertiary; color: #fff;
  border-radius: $radius-md; font-weight: 600; border: none;
}
.btn-wrong {
  flex: 1; height: $touch-min; background: $color-error; color: #fff;
  border-radius: $radius-md; font-weight: 600; border: none;
}

.graded-result { margin-top: 8px; }
.result-badge {
  font-size: $font-body-md; font-weight: 600; padding: 4px 12px; border-radius: $radius-full;
}
.badge-correct { background: rgba($color-tertiary, 0.12); color: #166534; }
.badge-wrong { background: rgba($color-error, 0.12); color: #991b1b; }
.comment { font-size: $font-body-md; color: $color-on-surface-variant; margin-left: 8px; }

.empty { text-align: center; margin-top: 120px; }
.empty-text { font-size: $font-body-md; color: $color-on-surface-variant; }
</style>
