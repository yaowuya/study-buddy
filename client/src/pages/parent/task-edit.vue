<template>
  <view class="page">
    <!-- TopAppBar -->
    <view class="appbar" :style="{ paddingTop: Math.max(statusBarHeight, 12) + 'px' }">
      <view class="appbar-back" @tap="goBack">
        <text class="material-symbols-outlined">arrow_back</text>
      </view>
      <text class="appbar-title">编辑作业</text>
      <view class="appbar-placeholder"></view>
    </view>

    <scroll-view scroll-y class="main" :style="{ paddingTop: (Math.max(statusBarHeight, 12) + 56) + 'px' }">
      <!-- ========== 科目选择卡片 ========== -->
      <view class="card">
        <text class="card-heading">选择科目</text>
        <scroll-view scroll-x class="subject-scroll">
          <view class="subject-row">
            <view
              v-for="s in subjects" :key="s.value"
              :class="['subject-pill', form.subject === s.value ? `subject-pill-active subject-pill-${s.value}` : '']"
              @tap="selectSubject(s.value)"
            >
              <text class="material-symbols-outlined ms-pill-icon" :class="form.subject === s.value ? 'ms-fill' : ''">{{ s.icon }}</text>
              <text class="subject-pill-label">{{ s.label }}</text>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- ========== 作业标题卡片 ========== -->
      <view class="card">
        <text class="card-heading">为作业起个好名字</text>
        <input v-model="form.title" class="field-input" placeholder="输入作业标题" />
      </view>

      <!-- ========== 听写设置卡片 ========== -->
      <view class="dictation-card">
        <view class="dictation-header">
          <view class="dictation-title-row">
            <text class="material-symbols-outlined ms-dictation-icon">record_voice_over</text>
            <text class="card-heading dictation-heading">开启听写之旅</text>
          </view>
          <view :class="['toggle', dictationEnabled ? 'toggle-on' : '']" @tap="dictationEnabled = !dictationEnabled">
            <view class="toggle-thumb">
              <text v-if="dictationEnabled" class="material-symbols-outlined ms-toggle-check">check</text>
            </view>
          </view>
        </view>

        <view :class="['dictation-inner', dictationEnabled ? '' : 'dictation-inner-disabled']">
          <view class="word-input-row">
            <input v-model="wordInput" class="word-input" placeholder="输入需要听写的生字或单词..." @confirm="addWord" />
            <view class="add-word-btn" @tap="addWord">
              <text class="add-word-btn-text">添加</text>
            </view>
          </view>
          <view v-if="dictationWords.length > 0" class="word-tags">
            <view v-for="(w, i) in dictationWords" :key="i" class="word-tag">
              <text class="word-tag-text">{{ w }}</text>
              <text class="material-symbols-outlined ms-tag-close" @tap="removeWord(i)">close</text>
            </view>
          </view>
        </view>

        <text :class="['dictation-hint', dictationEnabled ? '' : 'dictation-hint-disabled']">
          输入需要听写的生字或单词，我们将为您生成专门的听写卡片。
        </text>
      </view>

      <!-- ========== 详细说明卡片 ========== -->
      <view class="card">
        <text class="card-heading">留下你的温馨提示</text>
        <textarea v-model="form.desc" class="field-textarea" placeholder="请详细描述作业的具体要求..." />
      </view>

      <!-- ========== 预计时长卡片 ========== -->
      <view class="card">
        <text class="card-heading">预计需要多长时间？（分钟）</text>
        <input v-model.number="form.duration" type="number" class="field-input" placeholder="例如：30" />
      </view>

      <!-- ========== 保存按钮 ========== -->
      <view class="submit-btn" @tap="handleSubmit">
        <text class="submit-text">保存修改</text>
      </view>

      <!-- ========== 删除按钮 ========== -->
      <view class="delete-btn" @tap="showDeleteConfirm = true">
        <text class="material-symbols-outlined delete-icon">delete</text>
        <text class="delete-text">删除任务</text>
      </view>

      <view class="bottom-spacer"></view>
    </scroll-view>

    <!-- ========== 删除确认弹窗 ========== -->
    <ConfirmModal
      v-model:visible="showDeleteConfirm"
      type="danger"
      icon="delete"
      title="确认删除？"
      desc="删除后作业内容将无法找回，确定要继续吗？"
      cancel-text="取消"
      confirm-text="确定删除"
      confirm-icon="delete"
      @confirm="confirmDelete"
    />

    <!-- Bottom Nav -->
    <BottomNav active="dashboard" :navItems="parentNavItems" />
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { getTask, updateTask, deleteTask } from '@/api/tasks'
import { getDictationItems, createDictationItems, deleteDictationItems } from '@/api/dictation'
import BottomNav from '@/components/BottomNav.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import type { NavItem } from '@/components/BottomNav.vue'

const parentNavItems: NavItem[] = [
  { key: 'dashboard', icon: 'assignment', label: '作业', url: '/pages/parent/dashboard' },
  { key: 'create', icon: 'calendar_today', label: '布置', url: '/pages/parent/task-create' },
  { key: 'grading', icon: 'history', label: '历史', url: '/pages/parent/grading' },
]

const taskId = ref('')
const statusBarHeight = ref(0)
const safeAreaBottom = ref(0)
const dictationEnabled = ref(false)
const dictationWords = ref<string[]>([])
const wordInput = ref('')
const showDeleteConfirm = ref(false)

const subjects = [
  { value: '语文', label: '语文', icon: 'menu_book' },
  { value: '数学', label: '数学', icon: 'calculate' },
  { value: '英语', label: '英语', icon: 'language' },
]

const form = reactive({
  title: '',
  desc: '',
  duration: null as number | null,
  subject: '语文' as string,
})

function selectSubject(subject: string) {
  form.subject = subject
}

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

function goBack() {
  uni.navigateBack({ fail: () => uni.redirectTo({ url: '/pages/parent/dashboard' }) })
}

async function loadTask() {
  if (!taskId.value) return
  try {
    const task = await getTask(taskId.value)
    form.title = task.title
    form.desc = task.desc || ''
    form.duration = task.duration
    form.subject = task.subject || '语文'

    // Load dictation items
    const items = await getDictationItems(taskId.value)
    if (items.length > 0) {
      dictationEnabled.value = true
      dictationWords.value = items.map(i => i.content)
    }
  } catch (e: any) {
    uni.showToast({ title: e.message || '加载失败', icon: 'none' })
  }
}

async function handleSubmit() {
  if (!form.title.trim()) {
    uni.showToast({ title: '请输入任务标题', icon: 'none' })
    return
  }
  try {
    await updateTask(taskId.value, {
      title: form.title,
      desc: form.desc || undefined,
      duration: form.duration || undefined,
      subject: form.subject || undefined,
    })
    // Update dictation items
    await deleteDictationItems(taskId.value)
    if (dictationEnabled.value && dictationWords.value.length > 0) {
      await createDictationItems(taskId.value, dictationWords.value.map(w => ({ content: w })))
    }
    uni.showToast({ title: '保存成功', icon: 'success' })
    setTimeout(() => uni.redirectTo({ url: '/pages/parent/dashboard' }), 500)
  } catch (e: any) {
    uni.showToast({ title: e.message || '保存失败', icon: 'none' })
  }
}

async function confirmDelete() {
  try {
    await deleteDictationItems(taskId.value)
    await deleteTask(taskId.value)
    showDeleteConfirm.value = false
    uni.showToast({ title: '删除成功', icon: 'success' })
    setTimeout(() => uni.redirectTo({ url: '/pages/parent/dashboard' }), 500)
  } catch (e: any) {
    showDeleteConfirm.value = false
    uni.showToast({ title: e.message || '删除失败', icon: 'none' })
  }
}

onLoad((query) => {
  taskId.value = query?.id || ''
})

onMounted(() => {
  const info = uni.getSystemInfoSync()
  statusBarHeight.value = info.statusBarHeight || 0
  safeAreaBottom.value = info.safeAreaInsets?.bottom || 0
  loadTask()
})
</script>

<style lang="scss" scoped>
@use '@/static/styles/variables.scss' as *;

// ================================================================
// 主题色 (Soft Organic Cards 风格，与 task-create 一致)
// ================================================================
$green-primary: #4CAF50;
$green-light: #81C784;
$green-secondary-container: #dcfce7;
$green-tag-container: #b7eea5;
$green-fixed: #baf1a7;

$surface-bg: #F8F9FB;
$surface-card: #ffffff;
$surface-field: #f1f5f9;

$on-surface: #1e293b;
$on-surface-variant: #475569;
$outline-variant: #e2e8f0;
$dark-green: #3a692e;
$on-secondary-fixed-variant: #225119;

// ================================================================
// Material Symbols Outlined
// ================================================================
.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-weight: normal;
  font-style: normal;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.ms-fill {
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

// ================================================================
// Page
// ================================================================
.page { min-height: 100vh; background: $surface-bg; }

// ================================================================
// TopAppBar (带返回箭头)
// ================================================================
.appbar {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba($outline-variant, 0.5);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; padding-bottom: 12px;
  height: 56px; box-sizing: content-box;
}
.appbar-back {
  width: 40px; height: 40px; border-radius: 9999px;
  display: flex; align-items: center; justify-content: center;
  color: $dark-green;
  &:active { background: rgba($green-primary, 0.1); }
}
.appbar-back .material-symbols-outlined { font-size: 24px; color: $dark-green; }
.appbar-title {
  font-size: 24px; font-weight: 600; color: $dark-green;
  letter-spacing: -0.02em; position: absolute; left: 50%; transform: translateX(-50%);
}
.appbar-placeholder { width: 40px; }

// ================================================================
// Main
// ================================================================
.main { flex: 1; padding: 0 24px; box-sizing: border-box; width: 100%; padding-bottom: 128px; }

// ================================================================
// Cards
// ================================================================
.card {
  background: $surface-card; border-radius: 24px; padding: 20px;
  border-bottom: 1px solid rgba($outline-variant, 0.4); margin-bottom: 20px;
}
.card-heading {
  font-size: 18px; font-weight: 600; color: $on-surface;
  margin-bottom: 12px; display: block; line-height: 24px;
}

// ================================================================
// Subject Pills (科目对应颜色)
// ================================================================
.subject-scroll { white-space: nowrap; }
.subject-row { display: flex; gap: 12px; padding-bottom: 4px; }
.subject-pill {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 14px; border-radius: 9999px;
  background: $surface-field; border: 1px solid rgba($outline-variant, 0.5);
  transition: all 0.2s; flex-shrink: 0;
}
.subject-pill-active { border-color: transparent; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.subject-pill-语文 { background: $color-soft-lilac; }
.subject-pill-语文 .ms-pill-icon { color: $dark-green; }
.subject-pill-数学 { background: $color-pale-peach; }
.subject-pill-数学 .ms-pill-icon { color: $dark-green; }
.subject-pill-英语 { background: $color-mint-light; }
.subject-pill-英语 .ms-pill-icon { color: $color-dark-green; }

.ms-pill-icon { font-size: 18px; color: $on-surface-variant; }
.subject-pill-label { font-size: 14px; font-weight: 500; color: $on-surface-variant; }
.subject-pill-active .subject-pill-label { font-weight: 600; }
.subject-pill-语文 .subject-pill-label { color: $dark-green; }
.subject-pill-数学 .subject-pill-label { color: $dark-green; }
.subject-pill-英语 .subject-pill-label { color: $color-dark-green; }

// ================================================================
// Form Fields
// ================================================================
.field-input {
  width: 100%; box-sizing: border-box;
  background: $surface-field; border: none; border-radius: 12px;
  padding: 14px 16px; font-size: 14px; color: $on-surface;
  min-height: 48px; box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.03);
}
.field-textarea {
  width: 100%; box-sizing: border-box;
  background: $surface-field; border: none; border-radius: 12px;
  padding: 14px 16px; font-size: 14px; color: $on-surface;
  height: 120px; box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.03);
}

// ================================================================
// Dictation Card
// ================================================================
.dictation-card {
  background: $surface-card; border-radius: 24px; padding: 20px; margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 4px 20px rgba(0,0,0,0.02);
  border: 1px solid $green-tag-container; position: relative; overflow: hidden;

  &::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(220,252,231,0.4) 0%, rgba(255,255,255,0) 100%);
    pointer-events: none; z-index: 0;
  }
}
.dictation-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; position: relative; z-index: 1; }
.dictation-title-row { display: flex; align-items: center; gap: 8px; }
.ms-dictation-icon { font-size: 24px; color: $dark-green; font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24; }
.dictation-heading { margin-bottom: 0; }

.dictation-inner {
  background: rgba(255,255,255,0.5); border-radius: 16px;
  position: relative; z-index: 1; transition: opacity 0.3s;
}
.dictation-inner-disabled { opacity: 0.5; pointer-events: none; }

.word-input-row { display: flex; gap: 8px; margin-bottom: 16px; }
.word-input {
  flex: 1; background: $surface-field; border: none; border-radius: 12px;
  padding: 12px 16px; font-size: 14px; color: $on-surface;
  min-height: 44px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.03);
}
.add-word-btn {
  display: flex; align-items: center; justify-content: center;
  background: $green-primary; color: #ffffff; padding: 12px 20px;
  border-radius: 12px; white-space: nowrap; box-shadow: 0 2px 8px rgba(76,175,80,0.15);
}
.add-word-btn-text { color: #ffffff; font-size: 14px; font-weight: 500; }

.word-tags { display: flex; flex-wrap: wrap; gap: 10px; }
.word-tag {
  display: flex; align-items: center; gap: 4px;
  padding: 6px 14px; border-radius: 9999px;
  background: rgba($green-tag-container, 0.5); border: 1px solid $green-tag-container;
}
.word-tag-text { font-size: 14px; font-weight: 500; color: $on-secondary-fixed-variant; margin-right: 4px; }
.ms-tag-close { font-size: 16px; color: rgba($on-secondary-fixed-variant, 0.5); }

.dictation-hint {
  font-size: 14px; color: $on-surface-variant; margin-top: 16px;
  position: relative; z-index: 1; display: block; line-height: 20px;
}
.dictation-hint-disabled { opacity: 0.5; }

// ================================================================
// Toggle Switch
// ================================================================
.toggle { width: 44px; height: 24px; border-radius: 9999px; background: $surface-field; position: relative; transition: background 0.2s; }
.toggle-on { background: $green-primary; }
.toggle-thumb {
  position: absolute; top: 2px; left: 2px; width: 20px; height: 20px;
  border-radius: 9999px; background: #ffffff; border: 1px solid #d1d5db;
  display: flex; align-items: center; justify-content: center; transition: transform 0.2s;
  .toggle-on & { transform: translateX(20px); border-color: #ffffff; }
}
.ms-toggle-check { font-size: 14px; color: #ffffff; line-height: 1; }

// ================================================================
// Save Button (薄荷绿渐变胶囊)
// ================================================================
.submit-btn {
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, $green-primary 0%, $green-light 100%);
  color: #ffffff; padding: 20px; border-radius: 9999px;
  margin-top: 16px; margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(76,175,80,0.3); transition: all 0.15s;
  &:active { transform: scale(0.98); box-shadow: 0 6px 16px rgba(76,175,80,0.4); }
}
.submit-text { color: #ffffff; font-size: 18px; font-weight: 600; line-height: 24px; }

// ================================================================
// Delete Button (柔和红色)
// ================================================================
.delete-btn {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  background: #ffdad6; color: #93000a; padding: 16px; border-radius: 9999px;
  margin-bottom: 40px; transition: all 0.15s;
  &:active { transform: scale(0.98); opacity: 0.9; }
}
.delete-icon { font-size: 20px; color: #93000a; }
.delete-text { font-size: 16px; font-weight: 600; color: #93000a; }

.bottom-spacer { height: 80px; }
</style>
