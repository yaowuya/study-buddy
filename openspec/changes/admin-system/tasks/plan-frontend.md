# 管理后台前端 — 执行计划

## 任务总览

| # | 任务 | 依赖 | 预计 |
|---|------|------|------|
| F1 | 项目脚手架：Vite + Vue3 + Ant Design Vue + TS | — | 5min |
| F2 | TypeScript 类型定义 | F1 | 3min |
| F3 | Axios 实例 + 拦截器 | F1 | 3min |
| F4 | API 模块：auth/users/families/tasks | F2,F3 | 5min |
| F5 | Pinia auth store | F4 | 3min |
| F6 | 路由 + 导航守卫 | F5 | 3min |
| F7 | AdminLayout 布局 | F6 | 5min |
| F8 | LoginView 登录页 | F5,F6 | 5min |
| F9 | DashboardView 仪表盘 | F4,F7 | 5min |
| F10 | UserListView 用户列表 | F4,F7 | 5min |
| F11 | UserDetailView 用户详情 | F4,F7 | 5min |
| F12 | FamilyListView 家庭列表 | F4,F7 | 5min |
| F13 | FamilyDetailView 家庭详情 | F4,F7 | 5min |
| F14 | TaskListView 任务列表 | F4,F7 | 5min |
| F15 | TaskDetailView 任务详情 | F4,F7 | 5min |
| F16 | PasswordView 修改密码 | F4,F7 | 3min |
| F17 | 工具函数 + 全局样式精修 | F8-F16 | 5min |
| F18 | ESLint + 构建验证 | F17 | 3min |

---

### 任务 F1：项目脚手架

**Files:**
- 创建：`admin/` 整个目录

**Reasoning:** 前端一切工作的基础。Vite + Vue3 + Ant Design Vue + TypeScript + Pinia 一次性安装完毕。

- [ ] **步骤 1：创建项目**

```bash
cd D:/01-code/study-buddy
npm create vite@latest admin -- --template vue-ts
cd admin
npm install
npm install ant-design-vue@4 @ant-design/icons-vue pinia vue-router@4 axios
```

- [ ] **步骤 2：配置 vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: { '@': '/src' },
  },
})
```

- [ ] **步骤 3：配置 main.ts 注册 Ant Design Vue + Pinia + Router**

- [ ] **步骤 4：删除脚手架默认文件**（HelloWorld.vue 等）

- [ ] **步骤 5：提交**

```bash
git add admin/
git commit -m "初始化管理后台前端脚手架"
```

---

### 任务 F2：TypeScript 类型定义

**Files:**
- 创建：`admin/src/types/api.ts`
- 创建：`admin/src/types/auth.ts`
- 创建：`admin/src/types/user.ts`
- 创建：`admin/src/types/family.ts`
- 创建：`admin/src/types/task.ts`

**Reasoning:** 类型先行，API 模块和页面组件都依赖这些类型定义。

- [ ] **步骤 1：创建类型文件**

内容直接抄录 design-frontend.md 中的 TypeScript 类型定义章节。

- [ ] **步骤 2：提交**

```bash
git add admin/src/types/
git commit -m "新增管理后台 TypeScript 类型定义"
```

---

### 任务 F3：Axios 实例 + 拦截器

**Files:**
- 创建：`admin/src/api/request.ts`

**Reasoning:** 所有 API 模块的基础，拦截器统一处理 token 注入和错误提示。

- [ ] **步骤 1：创建 Axios 实例**

**Script Outline:**
- `const instance = axios.create({ baseURL: '/api/v1/admin', timeout: 10000 })`
- 请求拦截：从 localStorage 读 token 附加到 Authorization
- 响应拦截：401 → logout, 403 → message.error('无权限'), 500+ → message.error('服务器错误'), 无响应 → message.error('网络异常')

- [ ] **步骤 2：提交**

```bash
git add admin/src/api/request.ts
git commit -m "新增 Axios 实例与全局拦截器"
```

---

### 任务 F4：API 模块封装

**Files:**
- 创建：`admin/src/api/auth.ts`
- 创建：`admin/src/api/users.ts`
- 创建：`admin/src/api/families.ts`
- 创建：`admin/src/api/tasks.ts`

**Reasoning:** 封装所有后端接口调用，页面只调用 API 函数，不直接操作 axios。

- [ ] **步骤 1：auth API**

```typescript
// login, getMe, changePassword
```

- [ ] **步骤 2：users API**

```typescript
// listUsers, getUser, updateUser, deleteUser
```

- [ ] **步骤 3：families API**

```typescript
// listFamilies, getFamily, deleteFamily
```

- [ ] **步骤 4：tasks API**

```typescript
// listTasks, getTask, deleteTask, getStats
```

- [ ] **步骤 5：提交**

```bash
git add admin/src/api/
git commit -m "新增管理后台 API 模块"
```

---

### 任务 F5：Pinia auth store

**Files:**
- 创建：`admin/src/stores/auth.ts`

- [ ] **步骤 1：实现 auth store**

**Script Outline:**
- `state: { token, adminInfo }`
- `getters: isLoggedIn`
- `actions: login(username, password), logout(), fetchMe()`

- [ ] **步骤 2：提交**

```bash
git add admin/src/stores/auth.ts
git commit -m "新增 Pinia auth store"
```

---

### 任务 F6：路由 + 导航守卫

**Files:**
- 创建：`admin/src/router/index.ts`

- [ ] **步骤 1：定义路由表**

| path | component | meta |
|------|-----------|------|
| `/login` | LoginView | public |
| `/` | DashboardView | auth |
| `/users` | UserListView | auth |
| `/users/:id` | UserDetailView | auth |
| `/families` | FamilyListView | auth |
| `/families/:id` | FamilyDetailView | auth |
| `/tasks` | TaskListView | auth |
| `/tasks/:id` | TaskDetailView | auth |
| `/password` | PasswordView | auth |

- [ ] **步骤 2：导航守卫** — 未登录跳 /login

- [ ] **步骤 3：提交**

```bash
git add admin/src/router/
git commit -m "新增管理后台路由与导航守卫"
```

---

### 任务 F7：AdminLayout 布局

**Files:**
- 创建：`admin/src/layouts/AdminLayout.vue`
- 创建：`admin/src/components/PageHeader.vue`

**Reasoning:** 后台所有页面的外框，侧边栏+顶栏+内容区。

**Template Outline:**
- `<a-layout>` 根容器
  - `<a-layout-sider>` 侧边栏 — `<a-menu>` 导航项（仪表盘/用户管理/家庭管理/作业管理/修改密码）
  - `<a-layout>`
    - `<a-layout-header>` 顶栏 — Logo + `<a-dropdown>` 用户名/退出
    - `<a-layout-content>` — `<router-view />`

**Script Outline:**
- `<script setup lang="ts">`
- `const router = useRouter()`
- `const authStore = useAuthStore()`
- `const selectedKeys = computed(() => [router.currentRoute.value.path])`
- `const handleLogout = () => authStore.logout()`

**Style Outline:**
- 侧边栏宽度 200px，深色主题
- 顶栏高度 48px，白色背景，`display: flex; align-items: center; justify-content: flex-end; padding: 0 24px`
- 内容区 `padding: 24px; background: #f0f2f5`

- [ ] **步骤 1：实现 AdminLayout**

- [ ] **步骤 2：提交**

```bash
git add admin/src/layouts/ admin/src/components/
git commit -m "新增管理后台布局组件"
```

---

### 任务 F8：LoginView 登录页

**Files:**
- 创建：`admin/src/views/login/LoginView.vue`

**Template Outline:**
- 页面根容器 `display: flex; justify-content: center; align-items: center; height: 100vh`
  - `<a-card title="管理后台登录" style="width: 400px">`
    - `<a-form>` — `<a-form-item>` × 2（用户名 a-input + 密码 a-input-password）
    - `<a-button type="primary" html-type="submit" :loading="loading" block>` 登录

**Script Outline:**
- `<script setup lang="ts">`
- `const form = reactive({ username: '', password: '' })`
- `const loading = ref(false)`
- `const authStore = useAuthStore()`
- `const router = useRouter()`
- `const handleLogin = async () => { loading.value = true; try { await authStore.login(...); router.push('/') } finally { loading.value = false } }`

**Visual Checks:**
- 卡片居中，宽度 400px
- 登录按钮全宽，loading 态正确

- [ ] **步骤 1：实现 LoginView**

- [ ] **步骤 2：提交**

---

### 任务 F9：DashboardView 仪表盘

**Files:**
- 创建：`admin/src/views/dashboard/DashboardView.vue`

**Template Outline:**
- `<page-header title="仪表盘" />`
- `<a-row :gutter="16">`
  - `<a-col :span="6">` × 4 — `<a-card><a-statistic title="..." :value="..." /></a-card>`

**Script Outline:**
- `const stats = ref<AdminStatsOut | null>(null)`
- `onMounted(() => getStats().then(r => stats.value = r.data))`

**Style Outline:**
- a-row 使用 `gutter: 16`
- a-statistic 数值字号 24px

- [ ] **步骤 1：实现 DashboardView**

- [ ] **步骤 2：提交**

---

### 任务 F10：UserListView 用户列表

**Files:**
- 创建：`admin/src/views/users/UserListView.vue`

**Template Outline:**
- `<page-header title="用户管理" />`
- 搜索栏 `<a-space>`：`<a-input v-model:value="filters.phone" placeholder="手机号">`, `<a-select v-model:value="filters.role">`, `<a-select v-model:value="filters.isActive">`, `<a-button type="primary" @click="fetchData">搜索</a-button>`
- `<a-table :columns="columns" :data-source="data.items" :pagination="pagination" @change="handleTableChange">`
  - 列：手机号、角色（a-tag）、家庭邀请码、状态（a-badge）、操作（查看/禁用/删除 a-popconfirm）

**Script Outline:**
- `const filters = reactive({ phone: '', role: undefined, isActive: undefined })`
- `const data = ref<PaginatedResponse<AdminUserOut>>({ total: 0, items: [], page: 1, page_size: 20 })`
- `const fetchData = async () => { ... }`
- `const handleToggleActive = async (user) => { ... }`
- `const handleDelete = async (user) => { ... }`
- `onMounted(fetchData)`

**Visual Checks:**
- 角色标签颜色：家长=蓝，学生=绿
- 状态 badge：启用=绿，禁用=红
- 操作按钮带 a-popconfirm

- [ ] **步骤 1：实现 UserListView**

- [ ] **步骤 2：提交**

---

### 任务 F11：UserDetailView 用户详情

**Files:**
- 创建：`admin/src/views/users/UserDetailView.vue`

**Template Outline:**
- `<page-header title="用户详情" :subtitle="user?.phone" />`
- `<a-card title="基本信息">` — `<a-descriptions>` 手机号/角色/状态/家庭邀请码
- 操作区：`<a-select>` 修改角色，`<a-button>` 禁用/启用，`<a-popconfirm>` + `<a-button danger>` 删除
- `<a-card title="关联任务">` — `<a-table>` 简化列表

**Script Outline:**
- `const route = useRoute()`
- `const user = ref<AdminUserDetailOut | null>(null)`
- `const tasks = ref<AdminTaskOut[]>([])`
- `onMounted(() => getUser(route.params.id).then(...))`

- [ ] **步骤 1：实现 UserDetailView**

- [ ] **步骤 2：提交**

---

### 任务 F12：FamilyListView 家庭列表

**Files:**
- 创建：`admin/src/views/families/FamilyListView.vue`

**Template Outline:**
- `<page-header title="家庭管理" />`
- 搜索栏：邀请码输入框 + 搜索按钮
- `<a-table>` 列：邀请码、成员数、操作（查看/删除）

- [ ] **步骤 1：实现 FamilyListView**

- [ ] **步骤 2：提交**

---

### 任务 F13：FamilyDetailView 家庭详情

**Files:**
- 创建：`admin/src/views/families/FamilyDetailView.vue`

**Template Outline:**
- `<page-header title="家庭详情" :subtitle="family?.code" />`
- `<a-card title="基本信息">` — `<a-descriptions>` 邀请码/成员数
- `<a-card title="成员列表">` — `<a-table>` 手机号/角色/状态

- [ ] **步骤 1：实现 FamilyDetailView**

- [ ] **步骤 2：提交**

---

### 任务 F14：TaskListView 任务列表

**Files:**
- 创建：`admin/src/views/tasks/TaskListView.vue`

**Template Outline:**
- `<page-header title="作业管理" />`
- 搜索栏：邀请码输入框 + 状态下拉 + 日期范围(a-range-picker) + 搜索按钮
- `<a-table>` 列：标题/类型/科目/状态(a-tag)/日期/操作

**Script Outline:**
- 邀请码搜索：前端输入邀请码，需先调后端查询 family_id（或在后端接口加 code 筛选参数）
- 状态标签颜色：pending=灰, in_progress=蓝, submitted=橙, graded=绿

**Visual Checks:**
- 状态 a-tag 颜色正确
- 日期范围选择器正常工作

- [ ] **步骤 1：实现 TaskListView**

- [ ] **步骤 2：提交**

---

### 任务 F15：TaskDetailView 任务详情

**Files:**
- 创建：`admin/src/views/tasks/TaskDetailView.vue`

**Template Outline:**
- `<page-header title="任务详情" :subtitle="task?.title" />`
- `<a-card title="基本信息">` — `<a-descriptions>` 标题/类型/科目/状态/日期/时长
- `<a-card title="提交信息" v-if="task?.submission">` — `<a-descriptions>` 批改结果/留言/提交时间
- `<a-card title="听写条目" v-if="task?.dictation_items?.length">` — `<a-table>` 内容/语速/暂停间隔

**Visual Checks:**
- 无提交时隐藏提交卡片
- 无听写条目时隐藏听写卡片

- [ ] **步骤 1：实现 TaskDetailView**

- [ ] **步骤 2：提交**

---

### 任务 F16：PasswordView 修改密码

**Files:**
- 创建：`admin/src/views/password/PasswordView.vue`

**Template Outline:**
- `<page-header title="修改密码" />`
- `<a-card style="max-width: 500px">`
  - `<a-form>` — 旧密码/新密码/确认新密码
  - `<a-button type="primary" html-type="submit">` 提交

**Script Outline:**
- `const form = reactive({ old_password: '', new_password: '', confirm_password: '' })`
- 提交前校验 new_password === confirm_password
- 成功后 message.success + authStore.logout()

- [ ] **步骤 1：实现 PasswordView**

- [ ] **步骤 2：提交**

---

### 任务 F17：工具函数 + 全局样式精修

**Files:**
- 创建：`admin/src/utils/format.ts`
- 修改：`admin/src/style.css` 或 `admin/src/assets/`

**Reasoning:** 补全日期格式化、状态标签颜色映射等工具函数，全局样式微调。

- [ ] **步骤 1：format.ts** — `formatDate`, `roleLabel`, `roleColor`, `statusLabel`, `statusColor`

- [ ] **步骤 2：全局样式** — body 背景 `#f0f2f5`，去掉默认 margin

- [ ] **步骤 3：提交**

---

### 任务 F18：ESLint + 构建验证

**Reasoning:** 最终质量门禁，确保代码无 lint 错误，生产构建成功。

- [ ] **步骤 1：运行 ESLint**

```bash
cd admin && npm run lint
```

- [ ] **步骤 2：生产构建**

```bash
cd admin && npm run build
```

- [ ] **步骤 3：启动开发服务器手动验证**

```bash
cd admin && npm run dev
```

访问 http://localhost:5174 ，验证：
- 登录页正常显示
- 登录后跳转仪表盘
- 侧边栏导航正常
- 各列表页分页/筛选正常
- 详情页数据展示正确

- [ ] **步骤 4：最终提交**

```bash
git add admin/
git commit -m "管理后台前端完成：ESLint + 构建验证通过"
```
