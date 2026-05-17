<template>
  <view class="page">
    <!-- AppBar -->
    <view class="appbar" :style="{ paddingTop: Math.max(statusBarHeight, 12) + 'px' }">
      <view class="appbar-left">
        <view class="avatar-circle">
          <text class="material-symbols-outlined">face</text>
        </view>
        <text class="appbar-title">作业伙伴</text>
      </view>
      <text class="appbar-brand">布置新任务</text>
    </view>

    <scroll-view scroll-y class="main" :style="{ paddingTop: (Math.max(statusBarHeight, 12) + 56) + 'px' }">
      <!-- Page Title -->
      <view class="page-header">
        <text class="page-title">布置新任务</text>
        <text class="page-subtitle">为您孩子的每日学习计划添加新内容。</text>
      </view>

      <!-- Basic Info Card -->
      <view class="card">
        <!-- Task Title -->
        <view class="field-group">
          <view class="field-label">
            <text class="material-symbols-outlined field-icon">title</text>
            <text class="label-text">任务标题</text>
          </view>
          <input v-model="form.title" class="field-input" placeholder="例如：完成课后练习题" />
        </view>

        <!-- Subject Selection -->
        <view class="field-group">
          <view class="field-label">
            <text class="material-symbols-outlined field-icon">category</text>
            <text class="label-text">科目选择</text>
          </view>
          <view class="subject-grid">
            <view v-for="s in subjects" :key="s.value"
              :class="['subject-chip', form.subject === s.value ? 'subject-chip-active' : '']"
              @tap="form.subject = s.value">
              <text class="material-symbols-outlined subject-chip-icon">{{ s.icon }}</text>
              <text class="subject-chip-label">{{ s.label }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Dictation Settings Card -->
      <view class="dictation-card">
        <view class="dictation-deco"></view>
        <view class="dictation-header">
          <view class="dictation-title-row">
            <view class="dictation-title-icon">
              <text class="material-symbols-outlined">spellcheck</text>
            </view>
            <text class="dictation-title">听写设置</text>
          </view>
          <view :class="['toggle', dictationEnabled ? 'toggle-on' : '']" @tap="dictationEnabled = !dictationEnabled">
            <view class="toggle-thumb"></view>
          </view>
        </view>
        <text class="dictation-desc">输入需要听写的生字或单词，我们将为您生成专门的听写卡片。</text>
        <view v-if="dictationEnabled" class="dictation-body">
          <view class="word-input-row">
            <input v-model="wordInput" class="word-input" placeholder="输入生字词..." @confirm="addWord" />
            <view class="add-word-btn" @tap="addWord">
              <text class="material-symbols-outlined">add</text>
              <text class="add-btn-text">添加</text>
            </view>
          </view>
          <view v-if="dictationWords.length > 0" class="word-tags">
            <view v-for="(w, i) in dictationWords" :key="i" class="word-tag">
              <text class="word-tag-text">{{ w }}</text>
              <text class="material-symbols-outlined word-tag-del" @tap="removeWord(i)">close</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Details Card -->
      <view class="card">
        <view class="field-group">
          <view class="field-label">
            <text class="material-symbols-outlined field-icon">description</text>
            <text class="label-text">详细说明</text>
          </view>
          <textarea v-model="form.desc" class="field-textarea" placeholder="请详细描述作业的具体要求..." />
        </view>
        <view class="field-group">
          <view class="field-label">
            <text class="material-symbols-outlined field-icon">timer</text>
            <text class="label-text">预计时长（分钟）</text>
          </view>
          <input v-model.number="form.duration" type="number" class="field-input" placeholder="例如：30" />
        </view>
      </view>

      <!-- Submit Button -->
      <view class="submit-btn" @tap="handleSubmit">
        <text class="material-symbols-outlined submit-icon">send</text>
        <text class="submit-text">发布作业</text>
      </view>

      <view class="bottom-spacer"></view>
    </scroll-view>

    <!-- Bottom Nav -->
    <view class="bottom-nav" :style="{ paddingBottom: safeAreaBottom + 'px' }">
      <view class="nav-item" @tap="goDashboard">
        <text class="material-symbols-outlined nav-icon">auto_stories</text>
        <text class="nav-label">作业</text>
      </view>
      <view class="nav-item nav-item-active">
        <text class="material-symbols-outlined nav-icon nav-icon-fill">add_circle</text>
        <text class="nav-label">布置</text>
      </view>
      <view class="nav-item" @tap="goGrading">
        <text class="material-symbols-outlined nav-icon">history</text>
        <text class="nav-label">历史</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { createTask } from '@/api/tasks'
import { createDictationItems } from '@/api/dictation'

const statusBarHeight = ref(0)
const safeAreaBottom = ref(0)
const dictationEnabled = ref(false)
const dictationWords = ref<string[]>([])
const wordInput = ref('')

const subjects = [
  { value: '语文', label: '语文', icon: 'language' },
  { value: '数学', label: '数学', icon: 'calculate' },
  { value: '英语', label: '英语', icon: 'school' },
]

const form = reactive({
  type: 'school' as 'school' | 'home',
  title: '',
  desc: '',
  duration: null as number | null,
  date: new Date().toISOString().slice(0, 10),
  subject: '语文' as string,
})

function addWord() {
  const w = wordInput.value.trim()
  if (w && !dictationWords.value.includes(w)) {
    dictationWords.value.push(w)
  }
  wordInput.value = ''
}

function removeWord(i: number) {
  dictationWords.value.splice(i, 1)
}

async function handleSubmit() {
  if (!form.title.trim()) {
    uni.showToast({ title: '请输入任务标题', icon: 'none' })
    return
  }
  try {
    const task = await createTask({
      type: form.type,
      title: form.title,
      desc: form.desc || undefined,
      duration: form.duration || undefined,
      date: form.date,
      subject: form.subject || undefined,
    })
    if (dictationEnabled.value && dictationWords.value.length > 0) {
      await createDictationItems(task.id, dictationWords.value.map(w => ({ content: w })))
    }
    uni.showToast({ title: '发布成功', icon: 'success' })
    setTimeout(() => uni.redirectTo({ url: '/pages/parent/dashboard' }), 500)
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

function goDashboard() {
  uni.redirectTo({ url: '/pages/parent/dashboard' })
}

function goGrading() {
  uni.redirectTo({ url: '/pages/parent/grading' })
}

onMounted(() => {
  const info = uni.getSystemInfoSync()
  statusBarHeight.value = info.statusBarHeight || 0
  safeAreaBottom.value = info.safeAreaInsets?.bottom || 0
})
</script>

<style lang="scss" scoped>
@use '@/static/styles/variables.scss' as *;

.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-weight: normal; font-style: normal; font-size: 24px; line-height: 1;
  letter-spacing: normal; text-transform: none; display: inline-block;
  white-space: nowrap; word-wrap: normal; direction: ltr;
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.page { min-height: 100vh; background: $color-surface; font-family: $font-family-body; }

.appbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: #fff; border-bottom: 2px solid #f1f5f9;
  display: flex; align-items: center; justify-content: space-between;
  padding-left: $spacing-margin; padding-right: $spacing-margin; padding-bottom: 12px; padding-top: 12px;
}
.appbar-left { display: flex; align-items: center; gap: $spacing-sm; }
.avatar-circle {
  width: 40px; height: 40px; border-radius: $radius-full;
  background: $color-surface-container-high; display: flex; align-items: center; justify-content: center;
  color: $color-primary; border: 1px solid $color-outline-variant;
}
.appbar-title { font-family: $font-family; font-size: 14px; font-weight: 700; color: #3b82f6; }
.appbar-brand { font-family: $font-family; font-size: 16px; font-weight: 800; color: #2563eb; }
.appbar-icon-btn {
  width: 40px; height: 40px; border-radius: $radius-full;
  display: flex; align-items: center; justify-content: center; color: #3b82f6;
}

.main { flex: 1; padding: 0 $spacing-md; box-sizing: border-box; width: 100%; }

.page-header { margin-bottom: $spacing-lg; }
.page-title { font-family: $font-family; font-size: $font-headline-xl; font-weight: 700; color: $color-on-surface; display: block; }
.page-subtitle { font-size: $font-body-md; color: $color-on-surface-variant; display: block; margin-top: 4px; }

.card {
  background: $color-surface-container-lowest; border-radius: 24px;
  padding: $spacing-md; border: 1px solid $color-surface-container-high;
  box-shadow: 0 8px 24px rgba(0, 88, 189, 0.04); margin-bottom: $spacing-lg;
  display: flex; flex-direction: column; gap: $spacing-md;
}

.field-group { display: flex; flex-direction: column; gap: $spacing-base; }
.field-label { display: flex; align-items: center; gap: $spacing-xs; }
.field-icon { font-size: 18px; color: $color-outline; }
.label-text { font-family: $font-family; font-size: $font-label-md; font-weight: 600; color: $color-on-surface; }
.field-input {
  width: 100%;
  box-sizing: border-box;
  background: $color-surface-bright; border: 2px solid $color-outline-variant;
  border-radius: $radius-xl; padding: $spacing-sm; font-size: $font-body-md; color: $color-on-surface;
  min-height: $touch-min;
}
.field-textarea {
  width: 100%;
  box-sizing: border-box;
  background: $color-surface-bright; border: 2px solid $color-outline-variant;
  border-radius: $radius-xl; padding: $spacing-sm; font-size: $font-body-md; color: $color-on-surface;
  height: 80px;
}

// Subject grid
.subject-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: $spacing-sm; }
.subject-chip {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: $spacing-xs; padding: $spacing-sm; border-radius: $radius-xl;
  border: 2px solid $color-outline-variant; background: $color-surface-bright; color: $color-on-surface-variant;
  border-bottom: 4px solid $color-outline-variant;
}
.subject-chip-active {
  border-color: $color-primary; background: $color-primary-fixed; color: $color-primary-container;
  border-bottom-color: $color-on-primary-fixed-variant;
}
.subject-chip-icon { font-size: 24px; }
.subject-chip-label { font-family: $font-family; font-size: $font-label-sm; }

// Dictation card
.dictation-card {
  background: #f0fdf4; border-radius: 24px; padding: $spacing-md;
  border: 2px solid #bbf7d0; box-shadow: 0 8px 24px rgba(34, 197, 94, 0.06);
  margin-bottom: $spacing-lg; position: relative; overflow: hidden;
  display: flex; flex-direction: column; gap: $spacing-md;
}
.dictation-deco {
  position: absolute; right: -16px; top: -16px; width: 96px; height: 96px;
  background: rgba(187, 247, 208, 0.4); border-radius: $radius-full;
  filter: blur(24px); pointer-events: none;
}
.dictation-header { display: flex; align-items: center; justify-content: space-between; position: relative; z-index: 1; }
.dictation-title-row { display: flex; align-items: center; gap: $spacing-sm; color: #166534; }
.dictation-title-icon {
  background: #dcfce7; padding: 6px; border-radius: $radius-md;
  display: flex; align-items: center; justify-content: center;
  .material-symbols-outlined { font-size: 20px; color: #166534; }
}
.dictation-title { font-family: $font-family; font-size: 20px; font-weight: 600; color: #166534; }
.dictation-desc { font-size: 14px; line-height: 1.4; color: rgba(22, 101, 52, 0.8); position: relative; z-index: 1; }
.dictation-body { display: flex; flex-direction: column; gap: $spacing-sm; position: relative; z-index: 1; }
.word-input-row { display: flex; gap: $spacing-sm; }
.word-input {
  flex: 1; background: #fff; border: 2px solid #bbf7d0;
  border-radius: $radius-xl; padding: $spacing-sm; font-size: $font-body-md; color: $color-on-surface;
  min-height: $touch-min;
}
.add-word-btn {
  display: flex; align-items: center; justify-content: center; gap: $spacing-xs;
  background: #22c55e; color: #fff; padding: $spacing-sm $spacing-md;
  border-radius: $radius-xl; font-family: $font-family; font-size: $font-label-md; font-weight: 600;
  border-bottom: 3px solid #166534; min-height: $touch-min;
  &:active { border-bottom-width: 0; transform: translateY(3px); }
  .material-symbols-outlined { font-size: 18px; color: #fff; }
}
.add-btn-text { color: #fff; }
.word-tags { display: flex; flex-wrap: wrap; gap: $spacing-xs; }
.word-tag {
  display: flex; align-items: center; gap: $spacing-xs;
  padding: 6px 12px; border-radius: $radius-md; background: #fff;
  border: 1px solid #bbf7d0; font-family: $font-family; font-size: $font-label-sm; color: #166534;
}
.word-tag-text { color: #166534; }
.word-tag-del { font-size: 16px; color: #166534; }

// Toggle
.toggle {
  width: 44px; height: 24px; border-radius: $radius-full;
  background: $color-outline-variant; position: relative; transition: background 0.2s;
}
.toggle-on { background: #22c55e; }
.toggle-thumb {
  position: absolute; top: 2px; left: 2px; width: 20px; height: 20px;
  border-radius: $radius-full; background: #fff; transition: transform 0.2s;
  .toggle-on & { transform: translateX(20px); }
}

// Submit button (3D)
.submit-btn {
  display: flex; align-items: center; justify-content: center; gap: $spacing-sm;
  background: $color-primary; color: $color-on-primary;
  padding: $spacing-md; border-radius: 20px;
  border-bottom: 6px solid $color-on-primary-fixed-variant;
  font-family: $font-family; font-size: 20px; font-weight: 600;
  margin-bottom: $spacing-lg;
  &:active { border-bottom-width: 0; transform: translateY(6px); }
}
.submit-icon { font-size: 24px; color: $color-on-primary; }
.submit-text { color: $color-on-primary; }

.bottom-spacer { height: 100px; }

// Bottom Nav
.bottom-nav {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 100;
  background: #fff; border-top: 2px solid #f1f5f9;
  display: flex; justify-content: space-around; align-items: center;
  height: 80px; padding-left: $spacing-md; padding-right: $spacing-md;
}
.nav-item {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 6px 20px; color: #94a3b8;
}
.nav-item-active { background: #dbeafe; color: #1d4ed8; border-radius: $radius-2xl; }
.nav-icon { font-size: 24px; }
.nav-icon-fill { font-variation-settings: 'FILL' 1; }
.nav-label { font-family: $font-family; font-size: 12px; font-weight: 500; margin-top: 4px; }
</style>
