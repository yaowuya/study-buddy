<template>
  <view class="mistake-page">
    <view class="filter-bar">
      <view :class="['chip', !activeSubject ? 'chip-active' : '']" @tap="activeSubject = ''">
        <text>全部</text>
      </view>
      <view v-for="s in subjects" :key="s" :class="['chip', activeSubject === s ? 'chip-active' : '']" @tap="activeSubject = s">
        <text>{{ s }}</text>
      </view>
    </view>

    <view v-if="mistakes.length === 0" class="empty">
      <text class="empty-text">暂无错题记录</text>
    </view>

    <view v-else class="mistake-list">
      <view v-for="m in mistakes" :key="m.id" class="mistake-card">
        <text class="mistake-subject">{{ m.subject || '未分类' }}</text>
        <text class="mistake-task-id">任务 {{ m.task_id.slice(0, 8) }}</text>
        <button v-if="!m.archived" class="btn-archive" @tap="handleArchive(m.id)">归档</button>
        <text v-else class="archived-tag">已归档</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { listMistakes, archiveMistake } from '@/api/mistakes'
import type { MistakeOut } from '@/api/mistakes'

const subjects = ['语文', '数学', '英语']
const activeSubject = ref('')
const mistakes = ref<MistakeOut[]>([])

async function fetchMistakes() {
  try {
    mistakes.value = await listMistakes(activeSubject.value || undefined)
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

async function handleArchive(id: string) {
  try {
    await archiveMistake(id)
    await fetchMistakes()
    uni.showToast({ title: '已归档', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

watch(activeSubject, fetchMistakes)
onMounted(fetchMistakes)
</script>

<style lang="scss" scoped>
@use '@/static/styles/variables.scss' as *;

.mistake-page { padding: $spacing-md; min-height: 100vh; }

.filter-bar { display: flex; gap: 8px; margin-bottom: $spacing-md; flex-wrap: wrap; }
.chip {
  padding: 4px 16px; border-radius: $radius-full; font-size: $font-label;
  background: rgba($color-primary, 0.06); color: $color-on-surface-variant;
}
.chip-active { background: $color-primary; color: #fff; }

.mistake-list { display: flex; flex-direction: column; gap: $spacing-sm; }
.mistake-card {
  display: flex; align-items: center; gap: $spacing-sm;
  padding: $spacing-sm $card-padding; background: #fff; border-radius: $radius-lg;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.mistake-subject { font-size: $font-label; font-weight: 600; color: $color-primary; min-width: 40px; }
.mistake-task-id { flex: 1; font-size: $font-body-md; color: $color-on-surface-variant; }

.btn-archive {
  font-size: $font-label; padding: 4px 12px; background: transparent;
  color: $color-outline; border: 1px solid $color-outline-variant; border-radius: $radius-full;
}
.archived-tag { font-size: $font-label; color: $color-tertiary; }

.empty { text-align: center; margin-top: 120px; }
.empty-text { font-size: $font-body-md; color: $color-on-surface-variant; }
</style>
