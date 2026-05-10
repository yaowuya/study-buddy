# 客户端基础与认证 — 实现计划

> **For agentic workers:** REQUIRED SUB-KILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 初始化 UniApp (Vue 3 + TypeScript) 项目，搭建 API 层、状态管理、路由守卫和认证页面。

**Architecture:** UniApp + Vue 3 + Pinia + TypeScript。API 层统一封装 uni.request，Pinia 管理 auth/tasks/sync 状态。角色路由守卫分离家长端和学生端。

**Tech Stack:** UniApp, Vue 3, TypeScript, Pinia, uni-app 编译器

**前置:** `2026-05-10-backend-foundation.md` 已完成

---

## File Structure

```
client/
├── src/
│   ├── api/
│   │   ├── request.ts          # uni.request 封装
│   │   ├── auth.ts             # 认证接口
│   │   ├── tasks.ts            # 任务接口
│   │   ├── dictation.ts        # 听写接口
│   │   ├── submissions.ts      # 提交接口
│   │   └── mistakes.ts         # 错题接口
│   ├── stores/
│   │   ├── auth.ts             # 认证状态
│   │   ├── tasks.ts            # 任务状态
│   │   └── sync.ts             # 轮询同步
│   ├── composables/
│   │   └── useTTS.ts           # 本地 TTS
│   ├── utils/
│   │   └── storage.ts          # 本地存储工具
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── login.vue
│   │   │   └── bind.vue
│   │   ├── parent/
│   │   │   ├── dashboard.vue
│   │   │   ├── task-create.vue
│   │   │   ├── dictation-config.vue
│   │   │   ├── grading.vue
│   │   │   └── mistake-book.vue
│   │   └── student/
│   │       ├── home.vue
│   │       └── dictation.vue
│   ├── static/
│   │   └── styles/
│   │       └── variables.scss
│   ├── App.vue
│   ├── main.ts
│   └── manifest.json
├── pages.json
├── tsconfig.json
├── vite.config.ts
└── package.json
```

---

### Task 1: UniApp 项目初始化

**Files:**
- Create: 整个 `client/` 目录结构

- [ ] **Step 1: 使用 HBuilderX 或 CLI 创建项目**

如果使用 CLI（推荐）：

```bash
cd D:/01-code/study-buddy
npx degit dcloudio/uni-preset-vue#vite-ts client
```

如果使用 HBuilderX：新建项目 → Vue3 → TypeScript → 命名为 client。

- [ ] **Step 2: 安装依赖**

```bash
cd D:/01-code/study-buddy/client
npm install pinia
```

- [ ] **Step 3: 创建目录结构**

```bash
mkdir -p src/api src/stores src/composables src/utils src/static/styles
```

- [ ] **Step 4: 提交**

```bash
cd D:/01-code/study-buddy
git add client/
git commit -m "feat(client): initialize UniApp project with Vue3 + TypeScript"
```

---

### Task 2: 全局样式变量

**Files:**
- Create: `client/src/static/styles/variables.scss`

- [ ] **Step 1: 创建设计系统变量**

```scss
// client/src/static/styles/variables.scss

// Colors
$color-primary: #005DA7;
$color-primary-light: #4F46E5;
$color-secondary: #FFD95A;
$color-tertiary: #7ED957;
$color-error: #EF4444;
$color-surface: #f8f9fa;
$color-on-surface: #191c1d;
$color-on-surface-variant: #414751;
$color-outline: #717783;
$color-outline-variant: #c1c7d3;

// Typography
$font-family: 'Lexend', sans-serif;
$font-hero: 48px;
$font-card-title: 24px;
$font-body-lg: 18px;
$font-body-md: 16px;
$font-label: 14px;

// Spacing (8px grid)
$spacing-xs: 4px;
$spacing-sm: 12px;
$spacing-md: 24px;
$spacing-lg: 40px;
$spacing-xl: 64px;
$spacing-base: 8px;
$card-padding: 24px;

// Border Radius
$radius-sm: 0.25rem;
$radius-md: 0.75rem;
$radius-lg: 1rem;
$radius-xl: 1.5rem;
$radius-full: 9999px;

// Touch
$touch-min: 48px;
```

- [ ] **Step 2: 在 App.vue 中引入**

在 `client/src/App.vue` 的 `<style>` 中添加：

```scss
@import './static/styles/variables.scss';

page {
  font-family: $font-family;
  background-color: $color-surface;
  color: $color-on-surface;
}
```

- [ ] **Step 3: 提交**

```bash
cd D:/01-code/study-buddy
git add client/
git commit -m "feat(client): add design system SCSS variables"
```

---

### Task 3: API 请求封装

**Files:**
- Create: `client/src/api/request.ts`
- Create: `client/src/utils/storage.ts`

- [ ] **Step 1: 创建 storage 工具**

```typescript
// client/src/utils/storage.ts
const TOKEN_KEY = 'studybuddy_token'

export function getToken(): string | null {
  return uni.getStorageSync(TOKEN_KEY) || null
}

export function setToken(token: string): void {
  uni.setStorageSync(TOKEN_KEY, token)
}

export function removeToken(): void {
  uni.removeStorageSync(TOKEN_KEY)
}

export function setCache(key: string, data: any): void {
  uni.setStorageSync(key, JSON.stringify(data))
}

export function getCache<T = any>(key: string): T | null {
  const raw = uni.getStorageSync(key)
  if (!raw) return null
  try {
    return JSON.parse(raw) as T
  } catch {
    return null
  }
}
```

- [ ] **Step 2: 创建 request 封装**

```typescript
// client/src/api/request.ts
import { getToken, removeToken } from '@/utils/storage'

const BASE_URL = 'http://localhost:8000/api/v1'

interface ApiResponse<T = any> {
  code?: number
  data: T
  message?: string
}

export function request<T = any>(
  url: string,
  method: 'GET' | 'POST' | 'PATCH' | 'DELETE' = 'GET',
  data?: any,
): Promise<T> {
  return new Promise((resolve, reject) => {
    const token = getToken()
    const header: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }

    uni.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header,
      success: (res) => {
        if (res.statusCode === 401) {
          removeToken()
          uni.reLaunch({ url: '/pages/auth/login' })
          reject(new Error('Unauthorized'))
          return
        }
        if (res.statusCode >= 400) {
          const msg = (res.data as any)?.detail || `HTTP ${res.statusCode}`
          reject(new Error(msg))
          return
        }
        resolve(res.data as T)
      },
      fail: (err) => {
        reject(new Error(err.errMsg))
      },
    })
  })
}
```

- [ ] **Step 3: 提交**

```bash
cd D:/01-code/study-buddy
git add client/
git commit -m "feat(client): add API request wrapper and storage utils"
```

---

### Task 4: 认证 API 和 Store

**Files:**
- Create: `client/src/api/auth.ts`
- Create: `client/src/stores/auth.ts`

- [ ] **Step 1: 创建 auth API**

```typescript
// client/src/api/auth.ts
import { request } from './request'

export interface RegisterParams {
  phone: string
  password: string
  role: 'parent' | 'student'
}

export interface LoginParams {
  phone: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface UserOut {
  id: string
  phone: string
  role: 'parent' | 'student'
  family_id: string | null
}

export interface FamilyOut {
  id: string
  code: string
}

export function register(data: RegisterParams) {
  return request<TokenResponse>('/auth/register', 'POST', data)
}

export function login(data: LoginParams) {
  return request<TokenResponse>('/auth/login', 'POST', data)
}

export function getMe() {
  return request<UserOut>('/auth/me', 'GET')
}

export function bindFamily(code: string) {
  return request<FamilyOut>('/auth/bind', 'POST', { code })
}

export function studentBindFamily(code: string) {
  return request<FamilyOut>('/auth/student-bind', 'POST', { code })
}
```

- [ ] **Step 2: 创建 auth store**

```typescript
// client/src/stores/auth.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { setToken, removeToken, getToken } from '@/utils/storage'
import * as authApi from '@/api/auth'
import type { UserOut } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserOut | null>(null)
  const loading = ref(false)

  async function register(phone: string, password: string, role: 'parent' | 'student') {
    loading.value = true
    try {
      const res = await authApi.register({ phone, password, role })
      setToken(res.access_token)
      await fetchMe()
    } finally {
      loading.value = false
    }
  }

  async function login(phone: string, password: string) {
    loading.value = true
    try {
      const res = await authApi.login({ phone, password })
      setToken(res.access_token)
      await fetchMe()
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    try {
      user.value = await authApi.getMe()
    } catch {
      user.value = null
      removeToken()
    }
  }

  async function bind(code: string) {
    if (!user.value) return
    const fn = user.value.role === 'parent' ? authApi.bindFamily : authApi.studentBindFamily
    await fn(code)
    await fetchMe()
  }

  function logout() {
    user.value = null
    removeToken()
    uni.reLaunch({ url: '/pages/auth/login' })
  }

  async function init() {
    if (getToken()) {
      await fetchMe()
    }
  }

  const isParent = () => user.value?.role === 'parent'
  const isStudent = () => user.value?.role === 'student'
  const isBound = () => !!user.value?.family_id

  return { user, loading, register, login, fetchMe, bind, logout, init, isParent, isStudent, isBound }
})
```

- [ ] **Step 3: 提交**

```bash
cd D:/01-code/study-buddy
git add client/
git commit -m "feat(client): add auth API and Pinia store"
```

---

### Task 5: 认证页面

**Files:**
- Create: `client/src/pages/auth/login.vue`
- Create: `client/src/pages/auth/bind.vue`
- Modify: `client/pages.json`

- [ ] **Step 1: 配置 pages.json**

```json
{
  "pages": [
    { "path": "pages/auth/login", "style": { "navigationBarTitleText": "登录" } },
    { "path": "pages/auth/bind", "style": { "navigationBarTitleText": "绑定家庭" } },
    { "path": "pages/parent/dashboard", "style": { "navigationBarTitleText": "今日作业" } },
    { "path": "pages/parent/task-create", "style": { "navigationBarTitleText": "发布任务" } },
    { "path": "pages/parent/dictation-config", "style": { "navigationBarTitleText": "听写配置" } },
    { "path": "pages/parent/grading", "style": { "navigationBarTitleText": "作业批改" } },
    { "path": "pages/parent/mistake-book", "style": { "navigationBarTitleText": "错题本" } },
    { "path": "pages/student/home", "style": { "navigationBarTitleText": "今日任务" } },
    { "path": "pages/student/dictation", "style": { "navigationBarTitleText": "听写模式" } }
  ],
  "globalStyle": {
    "navigationBarTextStyle": "black",
    "navigationBarBackgroundColor": "#f8f9fa",
    "backgroundColor": "#f8f9fa"
  }
}
```

- [ ] **Step 2: 创建登录页**

```vue
<!-- client/src/pages/auth/login.vue -->
<template>
  <view class="login-page">
    <view class="logo-section">
      <text class="app-title">作业陪伴助手</text>
    </view>

    <view class="form-section">
      <input v-model="phone" type="number" placeholder="手机号" class="input" maxlength="11" />
      <input v-model="password" type="safe-password" placeholder="密码" class="input" />

      <view class="role-selector">
        <view :class="['role-btn', role === 'parent' ? 'role-active' : '']" @tap="role = 'parent'">
          <text>家长</text>
        </view>
        <view :class="['role-btn', role === 'student' ? 'role-active' : '']" @tap="role = 'student'">
          <text>学生</text>
        </view>
      </view>

      <button class="btn-primary" :loading="authStore.loading" @tap="handleLogin">登录</button>
      <button class="btn-secondary" @tap="handleRegister">注册</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const phone = ref('')
const password = ref('')
const role = ref<'parent' | 'student'>('parent')

async function handleLogin() {
  if (!phone.value || !password.value) {
    uni.showToast({ title: '请输入手机号和密码', icon: 'none' })
    return
  }
  try {
    await authStore.login(phone.value, password.value)
    navigateByRole()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

async function handleRegister() {
  if (!phone.value || !password.value) {
    uni.showToast({ title: '请输入手机号和密码', icon: 'none' })
    return
  }
  try {
    await authStore.register(phone.value, password.value, role.value)
    navigateByRole()
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

function navigateByRole() {
  if (!authStore.isBound()) {
    uni.redirectTo({ url: '/pages/auth/bind' })
    return
  }
  if (authStore.isParent()) {
    uni.switchTab({ url: '/pages/parent/dashboard' })
  } else {
    uni.switchTab({ url: '/pages/student/home' })
  }
}
</script>

<style lang="scss" scoped>
@import '@/static/styles/variables.scss';

.login-page {
  padding: $spacing-xl $spacing-md;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.logo-section { text-align: center; margin-bottom: $spacing-lg; }
.app-title { font-size: $font-hero; font-weight: 700; color: $color-primary; }

.form-section { display: flex; flex-direction: column; gap: $spacing-sm; }

.input {
  height: $touch-min;
  padding: 0 $spacing-sm;
  border: 1px solid $color-outline-variant;
  border-radius: $radius-md;
  font-size: $font-body-md;
  background: #fff;
}

.role-selector { display: flex; gap: $spacing-sm; }
.role-btn {
  flex: 1;
  height: $touch-min;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid $color-outline-variant;
  border-radius: $radius-md;
  font-size: $font-body-md;
  font-weight: 500;
}
.role-active {
  border-color: $color-primary;
  background: rgba($color-primary, 0.08);
  color: $color-primary;
}

.btn-primary {
  height: $touch-min;
  background: $color-primary;
  color: #fff;
  border-radius: $radius-md;
  font-size: $font-body-md;
  font-weight: 600;
  border: none;
}
.btn-secondary {
  height: $touch-min;
  background: transparent;
  color: $color-primary;
  border-radius: $radius-md;
  font-size: $font-body-md;
  border: 1px solid $color-primary;
}
</style>
```

- [ ] **Step 3: 创建绑定页**

```vue
<!-- client/src/pages/auth/bind.vue -->
<template>
  <view class="bind-page">
    <text class="title">输入家庭连接码</text>
    <text class="subtitle">请向家长获取6位连接码</text>
    <input v-model="code" type="number" placeholder="6位连接码" class="input" maxlength="6" />
    <button class="btn-primary" @tap="handleBind">绑定</button>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const code = ref('')

async function handleBind() {
  if (code.value.length !== 6) {
    uni.showToast({ title: '请输入6位连接码', icon: 'none' })
    return
  }
  try {
    await authStore.bind(code.value)
    if (authStore.isParent()) {
      uni.switchTab({ url: '/pages/parent/dashboard' })
    } else {
      uni.switchTab({ url: '/pages/student/home' })
    }
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}
</script>

<style lang="scss" scoped>
@import '@/static/styles/variables.scss';

.bind-page {
  padding: $spacing-xl $spacing-md;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
}

.title { font-size: $font-card-title; font-weight: 600; }
.subtitle { font-size: $font-body-md; color: $color-on-surface-variant; }

.input {
  width: 200px;
  height: $touch-min;
  text-align: center;
  font-size: 24px;
  letter-spacing: 12px;
  border: 2px solid $color-primary;
  border-radius: $radius-md;
  background: #fff;
}

.btn-primary {
  width: 200px;
  height: $touch-min;
  background: $color-primary;
  color: #fff;
  border-radius: $radius-md;
  font-size: $font-body-md;
  font-weight: 600;
  border: none;
}
</style>
```

- [ ] **Step 4: 提交**

```bash
cd D:/01-code/study-buddy
git add client/
git commit -m "feat(client): add login and family bind pages"
```

---

### Task 6: 业务 API 层

**Files:**
- Create: `client/src/api/tasks.ts`
- Create: `client/src/api/dictation.ts`
- Create: `client/src/api/submissions.ts`
- Create: `client/src/api/mistakes.ts`

- [ ] **Step 1: 创建 tasks API**

```typescript
// client/src/api/tasks.ts
import { request } from './request'

export interface TaskOut {
  id: string
  type: 'school' | 'home'
  title: string
  desc: string | null
  duration: number | null
  status: 'pending' | 'in_progress' | 'submitted' | 'graded'
  date: string
  subject: string | null
}

export interface TaskCreateParams {
  type: 'school' | 'home'
  title: string
  desc?: string
  duration?: number
  date: string
  subject?: string
}

export function createTask(data: TaskCreateParams) {
  return request<TaskOut>('/tasks/', 'POST', data)
}

export function listTasks(date: string) {
  return request<TaskOut[]>(`/tasks/?date=${date}`, 'GET')
}

export function getTask(id: string) {
  return request<TaskOut>(`/tasks/${id}`, 'GET')
}

export function updateTaskStatus(id: string, status: string) {
  return request<TaskOut>(`/tasks/${id}/status`, 'PATCH', { status })
}

export function deleteTask(id: string) {
  return request(`/tasks/${id}`, 'DELETE')
}
```

- [ ] **Step 2: 创建 dictation API**

```typescript
// client/src/api/dictation.ts
import { request } from './request'

export interface DictationItemOut {
  id: string
  task_id: string
  content: string
  speed: number
  pause_interval: number
}

export interface DictationItemCreate {
  content: string
  speed?: number
  pause_interval?: number
}

export function createDictationItems(taskId: string, items: DictationItemCreate[]) {
  return request<DictationItemOut[]>('/dictation/', 'POST', { task_id: taskId, items })
}

export function getDictationItems(taskId: string) {
  return request<DictationItemOut[]>(`/dictation/${taskId}`, 'GET')
}
```

- [ ] **Step 3: 创建 submissions API**

```typescript
// client/src/api/submissions.ts
import { request } from './request'

export interface SubmissionOut {
  id: string
  task_id: string
  comment: string | null
  is_correct: boolean | null
  submitted_at: string
}

export function submitTask(taskId: string) {
  return request<SubmissionOut>('/submissions/', 'POST', { task_id: taskId })
}

export function gradeSubmission(submissionId: string, isCorrect: boolean, comment?: string) {
  return request<SubmissionOut>(`/submissions/${submissionId}/grade`, 'POST', { is_correct: isCorrect, comment })
}
```

- [ ] **Step 4: 创建 mistakes API**

```typescript
// client/src/api/mistakes.ts
import { request } from './request'

export interface MistakeOut {
  id: string
  task_id: string
  subject: string | null
  archived: boolean
}

export function listMistakes(subject?: string, archived?: boolean) {
  const params = new URLSearchParams()
  if (subject) params.set('subject', subject)
  if (archived !== undefined) params.set('archived', String(archived))
  const qs = params.toString()
  return request<MistakeOut[]>(`/mistakes/${qs ? '?' + qs : ''}`, 'GET')
}

export function archiveMistake(id: string) {
  return request<MistakeOut>(`/mistakes/${id}/archive`, 'POST')
}
```

- [ ] **Step 5: 提交**

```bash
cd D:/01-code/study-buddy
git add client/
git commit -m "feat(client): add all business API modules"
```

---

### Task 7: Tasks Store 和 Sync Store

**Files:**
- Create: `client/src/stores/tasks.ts`
- Create: `client/src/stores/sync.ts`

- [ ] **Step 1: 创建 tasks store**

```typescript
// client/src/stores/tasks.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as tasksApi from '@/api/tasks'
import type { TaskOut } from '@/api/tasks'
import { setCache, getCache } from '@/utils/storage'

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref<TaskOut[]>([])
  const loading = ref(false)

  async function fetchTodayTasks() {
    loading.value = true
    try {
      const today = new Date().toISOString().slice(0, 10)
      tasks.value = await tasksApi.listTasks(today)
      setCache('today_tasks', tasks.value)
    } finally {
      loading.value = false
    }
  }

  async function updateStatus(taskId: string, status: string) {
    const updated = await tasksApi.updateTaskStatus(taskId, status)
    const idx = tasks.value.findIndex(t => t.id === taskId)
    if (idx !== -1) tasks.value[idx] = updated
    setCache('today_tasks', tasks.value)
    return updated
  }

  async function submitTask(taskId: string) {
    const { submitTask: apiSubmit } = await import('@/api/submissions')
    await apiSubmit(taskId)
    return updateStatus(taskId, 'submitted')
  }

  function loadCached() {
    const cached = getCache<TaskOut[]>('today_tasks')
    if (cached) tasks.value = cached
  }

  const pendingTasks = () => tasks.value.filter(t => t.status === 'pending')
  const allCompleted = () => tasks.value.length > 0 && tasks.value.every(t => t.status === 'submitted' || t.status === 'graded')

  return { tasks, loading, fetchTodayTasks, updateStatus, submitTask, loadCached, pendingTasks, allCompleted }
})
```

- [ ] **Step 2: 创建 sync store**

```typescript
// client/src/stores/sync.ts
import { defineStore } from 'pinia'
import { useTasksStore } from './tasks'

export const useSyncStore = defineStore('sync', () => {
  let timer: ReturnType<typeof setInterval> | null = null
  const INTERVAL = 30000

  function start() {
    if (timer) return
    const tasksStore = useTasksStore()
    tasksStore.fetchTodayTasks()
    timer = setInterval(() => {
      tasksStore.fetchTodayTasks()
    }, INTERVAL)
  }

  function stop() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  return { start, stop }
})
```

- [ ] **Step 3: 提交**

```bash
cd D:/01-code/study-buddy
git add client/
git commit -m "feat(client): add tasks store and polling sync store"
```

---

### Task 8: App.vue 初始化和路由守卫

**Files:**
- Modify: `client/src/App.vue`
- Modify: `client/src/main.ts`

- [ ] **Step 1: 更新 main.ts**

```typescript
// client/src/main.ts
import { createSSRApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

export function createApp() {
  const app = createSSRApp(App)
  app.use(createPinia())
  return { app }
}
```

- [ ] **Step 2: 更新 App.vue**

在 `App.vue` 的 `onLaunch` 中初始化 auth：

```vue
<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onLaunch(async () => {
  await authStore.init()
})
</script>
```

- [ ] **Step 3: 提交**

```bash
cd D:/01-code/study-buddy
git add client/
git commit -m "feat(client): add Pinia init and auth check on launch"
```
