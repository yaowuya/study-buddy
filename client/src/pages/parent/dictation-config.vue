<template>
  <view class="dict-config">
    <view class="form-section">
      <text class="section-title">听写词组</text>
      <textarea v-model="bulkText" placeholder="批量输入词组，每行一个词" class="textarea" />
      <button class="btn-secondary" @tap="parseBulk">解析词组</button>

      <view v-if="items.length" class="items-list">
        <view v-for="(item, idx) in items" :key="idx" class="item-row">
          <text class="item-index">{{ idx + 1 }}</text>
          <text class="item-content">{{ item.content }}</text>
          <text class="item-remove" @tap="items.splice(idx, 1)">&#10005;</text>
        </view>
      </view>

      <view class="speed-section">
        <text class="label">语速</text>
        <slider :value="speed * 100" :min="50" :max="200" :step="10" @change="onSpeedChange" />
        <text class="speed-val">{{ speed.toFixed(1) }}x</text>
      </view>

      <view class="pause-section">
        <text class="label">词间停顿</text>
        <slider :value="pauseInterval" :min="1" :max="10" :step="1" @change="onPauseChange" />
        <text class="pause-val">{{ pauseInterval }}秒</text>
      </view>

      <button class="btn-primary" @tap="handleSave">保存听写任务</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { createTask } from '@/api/tasks'
import { createDictationItems } from '@/api/dictation'

const bulkText = ref('')
const items = ref<{ content: string }[]>([])
const speed = ref(1.0)
const pauseInterval = ref(3)

function parseBulk() {
  const lines = bulkText.value.split('\n').map(l => l.trim()).filter(Boolean)
  if (lines.length === 0) {
    uni.showToast({ title: '请输入至少一个词组', icon: 'none' })
    return
  }
  items.value = lines.map(content => ({ content }))
}

function onSpeedChange(e: any) {
  speed.value = e.detail.value / 100
}

function onPauseChange(e: any) {
  pauseInterval.value = e.detail.value
}

async function handleSave() {
  if (items.value.length === 0) {
    uni.showToast({ title: '请先解析词组', icon: 'none' })
    return
  }
  try {
    const task = await createTask({
      type: 'school',
      title: '听写练习',
      date: new Date().toISOString().slice(0, 10),
      subject: '语文',
    })
    await createDictationItems(task.id, items.value.map(i => ({
      content: i.content,
      speed: speed.value,
      pause_interval: pauseInterval.value,
    })))
    uni.showToast({ title: '听写任务已发布', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 500)
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}
</script>

<style lang="scss" scoped>
@use '@/static/styles/variables.scss' as *;

.dict-config { padding: $spacing-md; }
.form-section { display: flex; flex-direction: column; gap: $spacing-sm; }
.section-title { font-size: $font-body-lg; font-weight: 600; }

.textarea {
  height: 120px; padding: 12px; border: 1px solid $color-outline-variant;
  border-radius: $radius-md; font-size: $font-body-md; background: #fff;
}

.items-list { display: flex; flex-direction: column; gap: 8px; }
.item-row {
  display: flex; align-items: center; gap: $spacing-sm; padding: 8px $spacing-sm;
  background: #fff; border-radius: $radius-md;
}
.item-index { font-size: $font-label; color: $color-outline; min-width: 20px; }
.item-content { flex: 1; font-size: $font-body-md; }
.item-remove { font-size: 16px; color: $color-error; padding: 8px; }

.speed-section, .pause-section { display: flex; align-items: center; gap: $spacing-sm; }
.label { font-size: $font-body-md; min-width: 80px; color: $color-on-surface-variant; }
.speed-val, .pause-val { font-size: $font-label; min-width: 40px; }

.btn-secondary {
  height: $touch-min; background: transparent; color: $color-primary;
  border-radius: $radius-md; font-size: $font-body-md; border: 1px solid $color-primary;
}
.btn-primary {
  height: $touch-min; background: $color-primary; color: #fff;
  border-radius: $radius-md; font-size: $font-body-md; font-weight: 600; border: none; margin-top: $spacing-md;
}
</style>
