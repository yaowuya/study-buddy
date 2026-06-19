<template>
  <view class="page">
    <!-- TopAppBar: 毛玻璃白底, 居中标题, 左汉堡/右占位 -->
    <view class="appbar" :style="{ paddingTop: Math.max(statusBarHeight, 12) + 'px' }">
      <view class="appbar-menu">
        <text class="material-symbols-outlined ms-menu">menu</text>
      </view>
      <text class="appbar-title">布置作业</text>
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
              :class="['subject-pill', form.subject === s.value ? 'subject-pill-active' : '']"
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

      <!-- ========== 听写设置卡片 (mint-gradient 特殊卡片) ========== -->
      <view class="dictation-card">
        <!-- 标题行 + 开关 -->
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

        <!-- 词汇输入区域 (毛玻璃内区) -->
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

        <!-- 提示文字 -->
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

      <!-- ========== 发布按钮 (绿色渐变胶囊) ========== -->
      <view class="submit-btn" @tap="handleSubmit">
        <text class="submit-text">发布作业</text>
      </view>

      <view class="bottom-spacer"></view>
    </scroll-view>

    <!-- ========== 底部浮动导航栏 ========== -->
    <BottomNav active="create" :navItems="parentNavItems" />
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { createTask } from '@/api/tasks'
import { createDictationItems } from '@/api/dictation'
import BottomNav from '@/components/BottomNav.vue'
import type { NavItem } from '@/components/BottomNav.vue'

const parentNavItems: NavItem[] = [
  { key: 'dashboard', icon: 'book', label: '作业', url: '/pages/parent/dashboard' },
  { key: 'create', icon: 'add_circle', label: '布置', url: '/pages/parent/task-create' },
  { key: 'grading', icon: 'history', label: '历史', url: '/pages/parent/grading' },
]

const statusBarHeight = ref(0)
const safeAreaBottom = ref(0)
const dictationEnabled = ref(false)
const dictationWords = ref<string[]>([])
const wordInput = ref('')

// 图标名对应 publish_job.html 的 Material Symbols
const subjects = [
  { value: '语文', label: '语文', icon: 'public' },
  { value: '数学', label: '数学', icon: 'calculate' },
  { value: '英语', label: '英语', icon: 'sort_by_alpha' },
]

function defaultTitle(subject: string): string {
  return subject
}

const form = reactive({
  type: 'school' as 'school' | 'home',
  title: defaultTitle('语文'),
  desc: '',
  duration: null as number | null,
  date: new Date().toISOString().slice(0, 10),
  subject: '语文' as string,
})

function selectSubject(subject: string) {
  const oldDefault = defaultTitle(form.subject)
  // 如果标题是空的，或等于旧科目的默认标题，就自动更新
  if (!form.title || form.title === oldDefault) {
    form.title = defaultTitle(subject)
  }
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

onMounted(() => {
  const info = uni.getSystemInfoSync()
  statusBarHeight.value = info.statusBarHeight || 0
  safeAreaBottom.value = info.safeAreaInsets?.bottom || 0
})
</script>

<style lang="scss" scoped>
@use '@/static/styles/variables.scss' as *;

// ================================================================
// 主题色 (直接对应 publish_job.html 的 Tailwind 配色)
// ================================================================
$green-primary: #4CAF50;
$green-light: #81C784;
$green-secondary-container: #dcfce7;
$green-tag-container: #b7eea5;
$green-fixed: #baf1a7;

$surface-bg: #f8fafc;
$surface-card: #ffffff;
$surface-field: #f1f5f9;
$surface-field-high: #f8fafc;

$on-surface: #1e293b;
$on-surface-variant: #475569;
$outline-variant: #e2e8f0;
$text-secondary: #6B7280;
$dark-green: #3a692e;
$on-secondary-fixed-variant: #225119;

// ================================================================
// Material Symbols Outlined 基础样式
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
.page {
  min-height: 100vh;
  background: $surface-bg;
  position: relative;
}

// ================================================================
// TopAppBar
// ================================================================
.appbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba($outline-variant, 0.5);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  padding-bottom: 12px;
  height: 56px;
  box-sizing: content-box;
}

.appbar-menu {
  width: 32px;
  display: flex;
  align-items: center;
}

.ms-menu {
  font-size: 24px;
  color: $on-surface;
}

.appbar-title {
  font-size: 24px;
  font-weight: 600;
  color: $on-surface;
  letter-spacing: -0.02em;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.appbar-placeholder {
  width: 32px;
}

// ================================================================
// Main Content
// ================================================================
.main {
  flex: 1;
  padding: 0 24px;
  box-sizing: border-box;
  width: 100%;
  padding-bottom: 128px;
}

// ================================================================
// Cards (白底 + 底部细线 + 无阴影)
// ================================================================
.card {
  background: $surface-card;
  border-radius: 24px;
  padding: 20px;
  border-bottom: 1px solid rgba($outline-variant, 0.4);
  margin-bottom: 20px;
}

.card-heading {
  font-size: 18px;
  font-weight: 600;
  color: $on-surface;
  margin-bottom: 12px;
  display: block;
  line-height: 24px;
}

// ================================================================
// Subject Pills
// - Active: bg-primary(#4CAF50) text-on-primary(#fff), icon FILL 1
// - Inactive: bg-surface-container(#f1f5f9) text-on-surface-variant(#475569), icon FILL 0
// ================================================================
.subject-scroll {
  white-space: nowrap;
}

.subject-row {
  display: flex;
  gap: 12px;
  padding-bottom: 4px;
}

.subject-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 9999px;
  background: $surface-field;
  border: 1px solid rgba($outline-variant, 0.5);
  transition: all 0.2s;
  flex-shrink: 0;
}

.subject-pill-active {
  background: $green-primary;
  border-color: $green-primary;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2);
}

.ms-pill-icon {
  font-size: 18px;
  color: $on-surface-variant;
}

.subject-pill-active .ms-pill-icon {
  color: #ffffff;
}

.subject-pill-label {
  font-size: 14px;
  font-weight: 500;
  color: $on-surface-variant;
}

.subject-pill-active .subject-pill-label {
  color: #ffffff;
  font-weight: 500;
}

// ================================================================
// Form Fields (浅灰底 + 内阴影 + 无边框)
// ================================================================
.field-input {
  width: 100%;
  box-sizing: border-box;
  background: $surface-field;
  border: none;
  border-radius: 12px;
  padding: 14px 16px;
  font-size: 14px;
  color: $on-surface;
  min-height: 48px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.03);
}

.field-textarea {
  width: 100%;
  box-sizing: border-box;
  background: $surface-field;
  border: none;
  border-radius: 12px;
  padding: 14px 16px;
  font-size: 14px;
  color: $on-surface;
  height: 120px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.03);
}

// ================================================================
// Dictation Card
// - shadow-card
// - border border-secondary-container (#b7eea5)
// - mint-gradient 伪元素
// - record_voice_over 图标 text-secondary (#3a692e) FILL 1
// ================================================================
.dictation-card {
  background: $surface-card;
  border-radius: 24px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 4px 20px rgba(0, 0, 0, 0.02);
  border: 1px solid $green-tag-container;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(220, 252, 231, 0.4) 0%, rgba(255, 255, 255, 0) 100%);
    pointer-events: none;
    z-index: 0;
  }
}

.dictation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  position: relative;
  z-index: 1;
}

.dictation-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

// record_voice_over 图标: FILL 1, text-secondary = #3a692e
.ms-dictation-icon {
  font-size: 24px;
  color: $dark-green;
  font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.dictation-heading {
  margin-bottom: 0;
}

// 词汇输入内区 (半透明毛玻璃)
.dictation-inner {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  position: relative;
  z-index: 1;
  transition: opacity 0.3s;
}

.dictation-inner-disabled {
  opacity: 0.5;
  pointer-events: none;
}

// 词汇输入行
.word-input-row {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.word-input {
  flex: 1;
  background: $surface-field;
  border: none;
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 14px;
  color: $on-surface;
  min-height: 44px;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.03);
}

.add-word-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: $green-primary;
  color: #ffffff;
  padding: 12px 20px;
  border-radius: 12px;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.15);
}

.add-word-btn-text {
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
}

// 词汇标签: bg-secondary-container/50, border-secondary-container, text-on-secondary-fixed-variant
.word-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.word-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border-radius: 9999px;
  background: rgba($green-tag-container, 0.5);
  border: 1px solid $green-tag-container;
}

.word-tag-text {
  font-size: 14px;
  font-weight: 500;
  color: $on-secondary-fixed-variant;
  margin-right: 4px;
}

// close 图标: text-on-secondary-fixed-variant/50
.ms-tag-close {
  font-size: 16px;
  color: rgba($on-secondary-fixed-variant, 0.5);
}

// 提示文字
.dictation-hint {
  font-size: 14px;
  color: $on-surface-variant;
  margin-top: 16px;
  position: relative;
  z-index: 1;
  display: block;
  line-height: 20px;
}

.dictation-hint-disabled {
  opacity: 0.5;
}

// ================================================================
// Toggle Switch
// - Off: bg-surface-container(#f1f5f9)
// - On: bg-primary(#4CAF50), 白色 thumb, check 图标白色 14px
// ================================================================
.toggle {
  width: 44px;
  height: 24px;
  border-radius: 9999px;
  background: $surface-field;
  position: relative;
  transition: background 0.2s;
}

.toggle-on {
  background: $green-primary;
}

.toggle-thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  border-radius: 9999px;
  background: #ffffff;
  border: 1px solid #d1d5db;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;

  .toggle-on & {
    transform: translateX(20px);
    border-color: #ffffff;
  }
}

.ms-toggle-check {
  font-size: 14px;
  color: #ffffff;
  line-height: 1;
}

// ================================================================
// Submit Button (publish-btn-gradient)
// ================================================================
.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, $green-primary 0%, $green-light 100%);
  color: #ffffff;
  padding: 20px;
  border-radius: 9999px;
  margin-top: 16px;
  margin-bottom: 40px;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
  transition: all 0.15s;

  &:active {
    transform: scale(0.98);
    box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
  }
}

.submit-text {
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
  line-height: 24px;
}

.bottom-spacer {
  height: 80px;
}

</style>
