<template>
  <view class="dashboard">
    <view class="header">
      <text class="greeting">今日作业</text>
      <text class="family-code" @tap="showCode = true">连接码：{{ familyCode }}</text>
    </view>

    <view v-if="tasks.length === 0" class="empty">
      <text class="empty-text">今天还没有任务，点击下方发布</text>
    </view>

    <view v-else class="task-list">
      <view v-for="task in tasks" :key="task.id" :class="['task-card', `task-${task.type}`]">
        <view class="task-header">
          <text :class="['task-type-badge', `badge-${task.type}`]">{{ task.type === 'school' ? '学校' : '家庭' }}</text>
          <text :class="['task-status', `status-${task.status}`]">{{ statusLabel(task.status) }}</text>
        </view>
        <text class="task-title">{{ task.title }}</text>
        <text v-if="task.desc" class="task-desc">{{ task.desc }}</text>
        <view class="task-footer">
          <text v-if="task.duration" class="task-duration">预计 {{ task.duration }} 分钟</text>
        </view>
      </view>
    </view>

    <view class="fab" @tap="goCreate">
      <text class="fab-text">+</text>
    </view>

    <view v-if="showCode" class="modal-overlay" @tap="showCode = false">
      <view class="modal-content" @tap.stop>
        <text class="modal-title">家庭连接码</text>
        <text class="modal-code">{{ familyCode }}</text>
        <text class="modal-hint">让学生输入此码完成绑定</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { useTasksStore } from '@/stores/tasks'
import { useSyncStore } from '@/stores/sync'

const authStore = useAuthStore()
const tasksStore = useTasksStore()
const syncStore = useSyncStore()
const showCode = ref(false)
const familyCode = ref('加载中')

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

const tasks = computed(() => tasksStore.tasks)

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '未开始', in_progress: '进行中', submitted: '待批改', graded: '已批改'
  }
  return map[status] || status
}

function goCreate() {
  uni.navigateTo({ url: '/pages/parent/task-create' })
}

onMounted(() => {
  tasksStore.loadCached()
  loadFamilyCode()
})

onShow(() => {
  tasksStore.fetchTodayTasks()
  syncStore.start()
})
</script>

<style lang="scss" scoped>
@import '@/static/styles/variables.scss';

.dashboard { padding: $spacing-md; min-height: 100vh; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: $spacing-md; }
.greeting { font-size: $font-card-title; font-weight: 600; }
.family-code { font-size: $font-label; color: $color-primary; }

.empty { text-align: center; margin-top: 120px; }
.empty-text { font-size: $font-body-md; color: $color-on-surface-variant; }

.task-list { display: flex; flex-direction: column; gap: $spacing-sm; }

.task-card {
  padding: $card-padding;
  background: #fff;
  border-radius: $radius-xl;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.task-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
.task-type-badge {
  font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: $radius-full; color: #fff;
}
.badge-school { background: $color-primary; }
.badge-home { background: #8B5CF6; }
.task-status { font-size: $font-label; font-weight: 500; }
.status-pending { color: $color-on-surface-variant; }
.status-in_progress { color: #F59E0B; }
.status-submitted { color: $color-primary; }
.status-graded { color: $color-tertiary; }

.task-title { font-size: $font-body-lg; font-weight: 600; }
.task-desc { font-size: $font-body-md; color: $color-on-surface-variant; margin-top: 4px; }
.task-footer { margin-top: 8px; }
.task-duration { font-size: $font-label; color: $color-outline; }

.fab {
  position: fixed; right: 24px; bottom: 80px;
  width: 56px; height: 56px; border-radius: 50%;
  background: $color-primary; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 93, 167, 0.3);
}
.fab-text { font-size: 28px; color: #fff; font-weight: 300; }

.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 999;
}
.modal-content {
  background: #fff; padding: $spacing-lg; border-radius: $radius-xl; text-align: center;
  width: 300px;
}
.modal-title { font-size: $font-card-title; font-weight: 600; display: block; margin-bottom: $spacing-md; }
.modal-code { font-size: 40px; font-weight: 700; color: $color-primary; letter-spacing: 8px; display: block; margin-bottom: $spacing-sm; }
.modal-hint { font-size: $font-body-md; color: $color-on-surface-variant; display: block; }
</style>
