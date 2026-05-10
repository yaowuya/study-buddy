# 客户端页面实现 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现家长端和学生端全部页面，包括任务管理、听写模式、批改、错题本和完成激励。

**Architecture:** 每个页面是独立的 Vue SFC，通过 Pinia store 和 API 层与后端交互。学生端强调大卡片大字体，家长端侧重信息密度。

**Tech Stack:** UniApp, Vue 3, TypeScript, Pinia

**前置:** `2026-05-10-client-foundation.md` 已完成

---

### Task 1: 家长端 — 今日任务总览页

**Files:**
- Create: `client/src/pages/parent/dashboard.vue`

- [ ] **Step 1: 创建家长 dashboard 页面**

```vue
<!-- client/src/pages/parent/dashboard.vue -->
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

    <!-- 家庭连接码弹窗 -->
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

const tasks = computed(() => tasksStore.tasks)
const familyCode = computed(() => authStore.user?.family_id ? '查看中' : '未绑定')

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
```

注意：`familyCode` 需要从后端获取，暂用占位。后续在 Task 5 中完善。

- [ ] **Step 2: 提交**

```bash
cd D:/01-code/study-buddy
git add client/
git commit -m "feat(client): add parent dashboard page"
```

---

### Task 2: 家长端 — 发布任务页

**Files:**
- Create: `client/src/pages/parent/task-create.vue`

- [ ] **Step 1: 创建发布任务页**

```vue
<!-- client/src/pages/parent/task-create.vue -->
<template>
  <view class="create-page">
    <view class="form-section">
      <view class="role-selector">
        <view :class="['role-btn', form.type === 'school' ? 'role-active-school' : '']" @tap="form.type = 'school'">
          <text>学校任务</text>
        </view>
        <view :class="['role-btn', form.type === 'home' ? 'role-active-home' : '']" @tap="form.type = 'home'">
          <text>家庭任务</text>
        </view>
      </view>

      <input v-model="form.title" placeholder="任务标题" class="input" />
      <textarea v-model="form.desc" placeholder="任务描述（选填）" class="textarea" />
      <input v-model.number="form.duration" type="number" placeholder="预计耗时（分钟，选填）" class="input" />

      <view class="subject-row">
        <text class="label">学科</text>
        <view class="chips">
          <view v-for="s in subjects" :key="s" :class="['chip', form.subject === s ? 'chip-active' : '']" @tap="form.subject = s">
            <text>{{ s }}</text>
          </view>
        </view>
      </view>

      <button class="btn-primary" @tap="handleSubmit">发布</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { createTask } from '@/api/tasks'

const subjects = ['语文', '数学', '英语']

const form = reactive({
  type: 'school' as 'school' | 'home',
  title: '',
  desc: '',
  duration: null as number | null,
  date: new Date().toISOString().slice(0, 10),
  subject: '' as string,
})

async function handleSubmit() {
  if (!form.title.trim()) {
    uni.showToast({ title: '请输入任务标题', icon: 'none' })
    return
  }
  try {
    await createTask({
      type: form.type,
      title: form.title,
      desc: form.desc || undefined,
      duration: form.duration || undefined,
      date: form.date,
      subject: form.subject || undefined,
    })
    uni.showToast({ title: '发布成功', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 500)
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}
</script>

<style lang="scss" scoped>
@import '@/static/styles/variables.scss';

.create-page { padding: $spacing-md; }
.form-section { display: flex; flex-direction: column; gap: $spacing-sm; }

.role-selector { display: flex; gap: $spacing-sm; }
.role-btn {
  flex: 1; height: $touch-min; display: flex; align-items: center; justify-content: center;
  border: 2px solid $color-outline-variant; border-radius: $radius-md; font-weight: 500;
}
.role-active-school { border-color: $color-primary; background: rgba($color-primary, 0.08); color: $color-primary; }
.role-active-home { border-color: #8B5CF6; background: rgba(#8B5CF6, 0.08); color: #8B5CF6; }

.input, .textarea {
  padding: 0 $spacing-sm; height: $touch-min; border: 1px solid $color-outline-variant;
  border-radius: $radius-md; font-size: $font-body-md; background: #fff;
}
.textarea { height: 80px; padding-top: 12px; }

.subject-row { display: flex; align-items: center; gap: $spacing-sm; }
.label { font-size: $font-body-md; color: $color-on-surface-variant; min-width: 40px; }
.chips { display: flex; gap: 8px; }
.chip {
  padding: 4px 12px; border-radius: $radius-full; font-size: $font-label;
  background: rgba($color-primary, 0.06); color: $color-on-surface-variant;
}
.chip-active { background: $color-primary; color: #fff; }

.btn-primary {
  height: $touch-min; background: $color-primary; color: #fff;
  border-radius: $radius-md; font-size: $font-body-md; font-weight: 600; border: none; margin-top: $spacing-md;
}
</style>
```

- [ ] **Step 2: 提交**

```bash
cd D:/01-code/study-buddy
git add client/
git commit -m "feat(client): add parent task create page"
```

---

### Task 3: 家长端 — 听写配置页

**Files:**
- Create: `client/src/pages/parent/dictation-config.vue`

- [ ] **Step 1: 创建听写配置页**

```vue
<!-- client/src/pages/parent/dictation-config.vue -->
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
          <text class="item-remove" @tap="items.splice(idx, 1)">✕</text>
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
@import '@/static/styles/variables.scss';

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
```

- [ ] **Step 2: 提交**

```bash
cd D:/01-code/study-buddy
git add client/
git commit -m "feat(client): add parent dictation config page"
```

---

### Task 4: 家长端 — 作业批改页

**Files:**
- Create: `client/src/pages/parent/grading.vue`

- [ ] **Step 1: 创建批改页**

```vue
<!-- client/src/pages/parent/grading.vue -->
<template>
  <view class="grading-page">
    <view class="tab-bar">
      <text :class="['tab', filter === 'submitted' ? 'tab-active' : '']" @tap="filter = 'submitted'">待批改</text>
      <text :class="['tab', filter === 'graded' ? 'tab-active' : '']" @tap="filter = 'graded'">已批改</text>
    </view>

    <view class="task-list">
      <view v-for="task in filteredTasks" :key="task.id" class="task-card">
        <text class="task-title">{{ task.title }}</text>
        <text class="task-type">{{ task.type === 'school' ? '学校' : '家庭' }}</text>

        <view v-if="task.status === 'submitted'" class="grade-actions">
          <button class="btn-correct" @tap="handleGrade(task, true)">✓ 正确</button>
          <button class="btn-wrong" @tap="handleGrade(task, false)">✕ 错误</button>
        </view>

        <view v-if="task.status === 'graded'" class="graded-result">
          <text :class="['result-badge', task._isCorrect ? 'badge-correct' : 'badge-wrong']">
            {{ task._isCorrect ? '✓ 正确' : '✕ 错误' }}
          </text>
          <text v-if="task._comment" class="comment">{{ task._comment }}</text>
        </view>
      </view>
    </view>

    <view v-if="filteredTasks.length === 0" class="empty">
      <text class="empty-text">{{ filter === 'submitted' ? '没有待批改的作业' : '没有已批改的记录' }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTasksStore } from '@/stores/tasks'
import { gradeSubmission } from '@/api/submissions'
import type { TaskOut } from '@/api/tasks'

const tasksStore = useTasksStore()
const filter = ref<'submitted' | 'graded'>('submitted')

interface GradedTask extends TaskOut {
  _submissionId?: string
  _isCorrect?: boolean
  _comment?: string
}

const filteredTasks = computed(() =>
  tasksStore.tasks.filter(t => t.status === filter.value) as GradedTask[]
)

async function handleGrade(task: GradedTask, isCorrect: boolean) {
  try {
    // 需要先获取 submission ID，这里简化处理
    const { request } = await import('@/api/request')
    const subs: any[] = await request(`/submissions/?task_id=${task.id}`)
    if (subs.length === 0) return
    await gradeSubmission(subs[0].id, isCorrect)
    await tasksStore.fetchTodayTasks()
    uni.showToast({ title: isCorrect ? '标记正确' : '标记错误', icon: 'success' })
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

onMounted(() => {
  tasksStore.fetchTodayTasks()
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
```

注意：后端缺少 `GET /submissions/?task_id=xxx` 的列表接口，需要在后端补充。

- [ ] **Step 2: 在后端 submissions.py 中补充按任务查询接口**

在 `backend/app/api/v1/submissions.py` 的路由列表中添加：

```python
@router.get("/", response_model=list[SubmissionOut])
def list_submissions(task_id: uuid.UUID | None = None, user: User = Depends(get_current_user_dependency), db: Session = Depends(get_db)):
    if not user.family_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Not bound to a family")
    q = db.query(Submission).join(Task, Submission.task_id == Task.id).filter(Task.family_id == user.family_id)
    if task_id:
        q = q.filter(Submission.task_id == task_id)
    return q.all()
```

并在文件顶部添加 `from app.models.task import Task` 的导入。

- [ ] **Step 3: 提交**

```bash
cd D:/01-code/study-buddy
git add client/ backend/
git commit -m "feat: add parent grading page and submission list API"
```

---

### Task 5: 家长端 — 错题本页

**Files:**
- Create: `client/src/pages/parent/mistake-book.vue`

- [ ] **Step 1: 创建错题本页**

```vue
<!-- client/src/pages/parent/mistake-book.vue -->
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

    <view class="mistake-list">
      <view v-for="m in mistakes" :key="m.id" class="mistake-card">
        <text class="mistake-subject">{{ m.subject || '未分类' }}</text>
        <text class="mistake-task-id">任务 {{ m.task_id.slice(0, 8) }}</text>
        <button v-if="!m.archived" class="btn-archive" @tap="handleArchive(m.id)">归档</button>
        <text v-else class="archived-tag">已归档</text>
      </view>
    </view>

    <view v-if="mistakes.length === 0" class="empty">
      <text class="empty-text">暂无错题记录</text>
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
@import '@/static/styles/variables.scss';

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
```

- [ ] **Step 2: 提交**

```bash
cd D:/01-code/study-buddy
git add client/
git commit -m "feat(client): add parent mistake book page"
```

---

### Task 6: 学生端 — 今日任务看板

**Files:**
- Create: `client/src/pages/student/home.vue`

- [ ] **Step 1: 创建学生首页**

```vue
<!-- client/src/pages/student/home.vue -->
<template>
  <view class="student-home">
    <text class="greeting">今日任务</text>

    <view v-if="tasks.length === 0" class="empty">
      <text class="empty-text">今天没有任务，休息一下吧！</text>
    </view>

    <view class="task-list">
      <view v-for="task in tasks" :key="task.id" :class="['task-card', `card-${task.type}`]" @tap="handleTaskTap(task)">
        <view class="card-top">
          <text :class="['type-pill', `pill-${task.type}`]">{{ task.type === 'school' ? '🏫 学校' : '🏠 家庭' }}</text>
          <text :class="['status-text', `st-${task.status}`]">{{ statusLabel(task.status) }}</text>
        </view>
        <text class="card-title">{{ task.title }}</text>
        <text v-if="task.desc" class="card-desc">{{ task.desc }}</text>
        <view v-if="task.duration" class="card-meta">
          <text class="duration">⏱ {{ task.duration }}分钟</text>
        </view>

        <view class="card-action">
          <button v-if="task.status === 'pending'" class="action-btn btn-start" @tap.stop="startTask(task)">开始</button>
          <button v-if="task.status === 'in_progress'" class="action-btn btn-done" @tap.stop="doneTask(task)">完成</button>
          <text v-if="task.status === 'submitted'" class="action-wait">等待批改</text>
          <text v-if="task.status === 'graded'" class="action-done">已完成</text>
        </view>
      </view>
    </view>

    <!-- 全部完成激励 -->
    <view v-if="showCelebration" class="celebration" @tap="showCelebration = false">
      <text class="celebration-emoji">🎉</text>
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
  // 跳转听写模式（如果该任务有听写项）
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
```

- [ ] **Step 2: 提交**

```bash
cd D:/01-code/study-buddy
git add client/
git commit -m "feat(client): add student home page with celebration"
```

---

### Task 7: 学生端 — 听写模式页 + TTS 封装

**Files:**
- Create: `client/src/composables/useTTS.ts`
- Create: `client/src/pages/student/dictation.vue`

- [ ] **Step 1: 创建 useTTS composable**

```typescript
// client/src/composables/useTTS.ts
import { ref } from 'vue'

export function useTTS() {
  const isPlaying = ref(false)
  const currentIndex = ref(-1)
  const words = ref<string[]>([])
  let timer: ReturnType<typeof setTimeout> | null = null

  // #ifdef APP-PLUS
  function speak(text: string, rate: number = 1.0): Promise<void> {
    return new Promise((resolve) => {
      const synth = plus.speech.createSpeechRecognizer({})
      plus.speech.startSpeak({ text, rate }, () => resolve())
    })
  }
  // #endif

  // #ifdef H5
  function speak(text: string, rate: number = 1.0): Promise<void> {
    return new Promise((resolve) => {
      const utter = new SpeechSynthesisUtterance(text)
      utter.rate = rate
      utter.lang = 'zh-CN'
      utter.onend = () => resolve()
      speechSynthesis.speak(utter)
    })
  }
  // #endif

  function setWords(list: string[]) {
    words.value = list
    currentIndex.value = -1
  }

  async function playSequence(rate: number = 1.0, pauseSeconds: number = 3) {
    isPlaying.value = true
    for (let i = 0; i < words.value.length; i++) {
      currentIndex.value = i
      await speak(words.value[i], rate)
      if (i < words.value.length - 1) {
        await delay(pauseSeconds * 1000)
      }
    }
    isPlaying.value = false
    currentIndex.value = -1
  }

  function delay(ms: number): Promise<void> {
    return new Promise(r => { timer = setTimeout(r, ms) })
  }

  function stop() {
    isPlaying.value = false
    currentIndex.value = -1
    if (timer) { clearTimeout(timer); timer = null }
    // #ifdef H5
    speechSynthesis.cancel()
    // #endif
  }

  function skipNext() {
    // 停止当前播放，playSequence 循环会继续下一个词
    // #ifdef H5
    speechSynthesis.cancel()
    // #endif
  }

  return { isPlaying, currentIndex, words, setWords, playSequence, stop, skipNext }
}
```

- [ ] **Step 2: 创建听写模式页**

```vue
<!-- client/src/pages/student/dictation.vue -->
<template>
  <view class="dictation-page">
    <view v-if="items.length === 0" class="empty">
      <text class="empty-text">该任务没有听写内容</text>
    </view>

    <view v-else class="dictation-content">
      <text class="word-display">{{ currentWord || '准备开始' }}</text>
      <text class="progress">{{ tts.currentIndex + 1 }} / {{ items.length }}</text>

      <view class="controls">
        <button class="ctrl-btn" @tap="handlePlay">{{ tts.isPlaying.value ? '暂停' : '开始' }}</button>
        <button class="ctrl-btn" @tap="handleReplay">重播</button>
        <button class="ctrl-btn" @tap="handleSkip">下一个</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getDictationItems } from '@/api/dictation'
import { useTTS } from '@/composables/useTTS'
import type { DictationItemOut } from '@/api/dictation'

const props = defineProps<{ taskId: string }>()
const items = ref<DictationItemOut[]>([])
const tts = useTTS()

const currentWord = computed(() => {
  if (tts.currentIndex.value < 0) return ''
  return items.value[tts.currentIndex.value]?.content || ''
})

async function loadItems() {
  try {
    items.value = await getDictationItems(props.taskId)
    tts.setWords(items.value.map(i => i.content))
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}

function handlePlay() {
  if (tts.isPlaying.value) {
    tts.stop()
  } else {
    const speed = items.value[0]?.speed || 1.0
    const pause = items.value[0]?.pause_interval || 3
    tts.playSequence(speed, pause)
  }
}

function handleReplay() {
  tts.stop()
  setTimeout(() => {
    const speed = items.value[0]?.speed || 1.0
    const pause = items.value[0]?.pause_interval || 3
    tts.playSequence(speed, pause)
  }, 300)
}

function handleSkip() {
  tts.skipNext()
}

onMounted(loadItems)
onUnmounted(() => tts.stop())
</script>

<style lang="scss" scoped>
@import '@/static/styles/variables.scss';

.dictation-page {
  min-height: 100vh; display: flex; flex-direction: column;
  align-items: center; justify-content: center; padding: $spacing-lg;
}

.word-display {
  font-size: 48px; font-weight: 500; color: $color-primary-light;
  letter-spacing: 0.05em; line-height: 1.5; text-align: center;
}

.progress {
  font-size: $font-body-lg; color: $color-on-surface-variant;
  margin-top: $spacing-md; margin-bottom: $spacing-lg;
}

.controls { display: flex; gap: $spacing-sm; }
.ctrl-btn {
  min-width: 80px; height: $touch-min; border-radius: $radius-md;
  font-size: $font-body-md; font-weight: 600; border: none;
  background: $color-primary; color: #fff;
}

.empty { text-align: center; }
.empty-text { font-size: $font-body-lg; color: $color-on-surface-variant; }
</style>
```

- [ ] **Step 3: 提交**

```bash
cd D:/01-code/study-buddy
git add client/
git commit -m "feat(client): add student dictation page with local TTS"
```
