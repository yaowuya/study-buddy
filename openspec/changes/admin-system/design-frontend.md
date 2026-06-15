# 管理后台前端 — 技术方案设计

## 技术栈

| 维度 | 选型 |
|------|------|
| 框架 | Vue 3 + TypeScript |
| UI 组件库 | Ant Design Vue 4.x |
| 构建工具 | Vite 5.x |
| 状态管理 | Pinia |
| 路由 | Vue Router 4 |
| HTTP | Axios |
| 代码规范 | ESLint + Prettier |

## 目录结构

```
admin/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── .eslintrc.cjs
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── api/                  # API 请求模块
│   │   ├── request.ts        # Axios 实例 + 拦截器
│   │   ├── auth.ts           # 管理员登录 / me / 改密
│   │   ├── users.ts          # 用户管理接口
│   │   ├── families.ts       # 家庭管理接口
│   │   └── tasks.ts          # 作业管理接口 + 统计
│   ├── types/                # TypeScript 类型定义
│   │   ├── api.ts            # 通用类型：PaginatedResponse 等
│   │   ├── auth.ts           # AdminOut, AdminLogin
│   │   ├── user.ts           # AdminUserOut, AdminUserDetailOut
│   │   ├── family.ts         # AdminFamilyOut, AdminFamilyDetailOut
│   │   └── task.ts           # AdminTaskOut, AdminTaskDetailOut, AdminStatsOut
│   ├── stores/               # Pinia stores
│   │   └── auth.ts           # 登录状态 + token
│   ├── router/
│   │   └── index.ts          # 路由定义 + 导航守卫
│   ├── layouts/
│   │   └── AdminLayout.vue   # 后台整体布局（侧边栏 + 顶栏 + 内容区）
│   ├── views/
│   │   ├── login/
│   │   │   └── LoginView.vue
│   │   ├── dashboard/
│   │   │   └── DashboardView.vue
│   │   ├── users/
│   │   │   ├── UserListView.vue
│   │   │   └── UserDetailView.vue
│   │   ├── families/
│   │   │   ├── FamilyListView.vue
│   │   │   └── FamilyDetailView.vue
│   │   ├── tasks/
│   │   │   ├── TaskListView.vue
│   │   │   └── TaskDetailView.vue
│   │   └── password/
│   │       └── PasswordView.vue        # 修改密码页面
│   ├── components/           # 公共组件
│   │   └── PageHeader.vue
│   └── utils/
│       └── format.ts         # 日期、状态等格式化工具
```

## 页面与路由

| 路径 | 页面 | 说明 | 权限 |
|------|------|------|------|
| `/login` | LoginView | 管理员登录 | 公开 |
| `/` | DashboardView | 仪表盘（概览统计） | 需登录 |
| `/users` | UserListView | 用户列表 | 需登录 |
| `/users/:id` | UserDetailView | 用户详情 | 需登录 |
| `/families` | FamilyListView | 家庭列表 | 需登录 |
| `/families/:id` | FamilyDetailView | 家庭详情 | 需登录 |
| `/tasks` | TaskListView | 任务列表 | 需登录 |
| `/tasks/:id` | TaskDetailView | 任务详情 | 需登录 |
| `/password` | PasswordView | 修改密码 | 需登录 |

## 布局设计

```
┌─────────────────────────────────────────────┐
│  顶栏：Logo + 管理员用户名 + 退出登录          │
├──────────┬──────────────────────────────────┤
│          │                                  │
│  侧边栏   │     内容区（router-view）          │
│          │                                  │
│  仪表盘   │                                  │
│  用户管理  │                                  │
│  家庭管理  │                                  │
│  作业管理  │                                  │
│  修改密码  │                                  │
│          │                                  │
└──────────┴──────────────────────────────────┘
```

使用 Ant Design Vue 的 `a-layout` + `a-layout-sider` + `a-menu` 实现。

## 页面设计详述

### 登录页 (LoginView)

- 居中卡片式登录表单
- 字段：用户名（a-input）、密码（a-input-password）
- 登录按钮：点击后调 `POST /api/v1/admin/auth/login`
- 成功后 token 存 localStorage，跳转首页
- 错误提示：a-message.error

### 仪表盘 (DashboardView)

- 四个统计卡片（a-card + a-statistic）：
  - 总用户数、总家庭数、今日任务数、待批改提交数
- 后续可扩展图表，当前只做数字统计
- API：`GET /api/v1/admin/stats`（返回 AdminStatsOut）

### 修改密码 (PasswordView)

- 表单字段：旧密码（a-input-password）、新密码（a-input-password）、确认新密码
- 提交调 `PATCH /api/v1/admin/auth/password`
- 成功后 a-message.success 提示，退出登录跳转登录页

### 用户列表 (UserListView)

- 搜索栏：手机号输入框（a-input）、角色下拉（a-select: 全部/家长/学生）、状态下拉（a-select: 全部/启用/禁用）
- 表格（a-table）：
  - 列：手机号、角色、所属家庭邀请码、状态（启用/禁用）、操作
  - 操作：查看详情、禁用/启用（a-popconfirm 确认）、删除（a-popconfirm 确认）
- 分页：a-table 内置分页，对接后端 page/page_size
- 标签：角色用 a-tag 颜色区分（家长=蓝、学生=绿），状态用 a-badge

### 用户详情 (UserDetailView)

- 基本信息卡片：手机号、角色、状态、所属家庭
- 操作按钮：修改角色（a-select）、禁用/启用、删除
- 关联数据：该用户的任务列表（简化 a-table，只显示标题、状态、日期）

### 家庭列表 (FamilyListView)

- 搜索栏：邀请码输入框
- 表格（a-table）：
  - 列：邀请码、成员数、创建时间、操作
  - 操作：查看详情、删除（a-popconfirm 确认）

### 家庭详情 (FamilyDetailView)

- 基本信息卡片：邀请码、成员数
- 成员列表（a-table）：手机号、角色、状态

### 任务列表 (TaskListView)

- 搜索栏：邀请码输入框（a-input，模糊搜索，而非填 UUID）、状态下拉（a-select）、日期范围（a-range-picker）
- 表格（a-table）：
  - 列：标题、类型、科目、状态、日期、所属家庭、操作
  - 操作：查看详情、删除
- 状态标签：a-tag 颜色区分（pending=灰、in_progress=蓝、submitted=橙、graded=绿）

### 任务详情 (TaskDetailView)

- 基本信息卡片：标题、类型、科目、状态、日期、时长、所属家庭
- 提交信息（如有）：批改结果、批改留言、提交时间
- 听写条目列表（a-table）：内容、语速、暂停间隔

## 状态管理

### auth store (Pinia)

```typescript
// stores/auth.ts
export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('admin_token') || '',
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
  actions: {
    async login(username: string, password: string) { ... },
    logout() {
      this.token = ''
      localStorage.removeItem('admin_token')
      router.push('/login')
    },
  },
})
```

## Axios 拦截器

```typescript
// api/request.ts
const instance = axios.create({
  baseURL: '/api/v1/admin',
  timeout: 10000,
})

// 请求拦截：自动附加 Bearer token
instance.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

// 响应拦截：401 自动跳转登录，其他错误统一提示
instance.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const auth = useAuthStore()
      auth.logout()
    } else if (err.response?.status === 403) {
      message.error('无权限执行此操作')
    } else if (err.response?.status >= 500) {
      message.error('服务器错误，请稍后重试')
    } else if (!err.response) {
      message.error('网络异常，请检查网络连接')
    }
    return Promise.reject(err)
  },
)
```

## 路由守卫

```typescript
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.path !== '/login' && !auth.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})
```

## Vite 代理配置

开发环境代理 API 请求到后端：

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

管理后台使用 5174 端口，避免与 UniApp 客户端的 5173 冲突。

## TypeScript 类型定义

```typescript
// types/api.ts — 通用类型
export interface PaginatedResponse<T> {
  total: number
  items: T[]
  page: number
  page_size: number
}

// types/auth.ts
export interface AdminOut {
  id: string
  username: string
  is_active: boolean
  created_at: string
}
export interface AdminLogin {
  username: string
  password: string
}
export interface AdminPasswordChange {
  old_password: string
  new_password: string
}

// types/user.ts
export interface AdminUserOut {
  id: string
  phone: string
  role: 'parent' | 'student'
  family_id: string | null
  is_active: boolean
  is_deleted: boolean
}
export interface AdminUserDetailOut extends AdminUserOut {
  family_code: string | null
  task_count: number
}

// types/family.ts
export interface AdminFamilyOut {
  id: string
  code: string
  member_count: number
  is_deleted: boolean
}
export interface AdminFamilyDetailOut extends AdminFamilyOut {
  members: AdminUserOut[]
}

// types/task.ts
export interface AdminTaskOut {
  id: string
  family_id: string
  type: 'school' | 'home'
  title: string
  status: 'pending' | 'in_progress' | 'submitted' | 'graded'
  date: string
  subject: string | null
  is_deleted: boolean
}
export interface AdminTaskDetailOut extends AdminTaskOut {
  desc: string | null
  duration: number | null
  submission: { is_correct: boolean | null; comment: string | null; submitted_at: string } | null
  dictation_items: { content: string; speed: number; pause_interval: number }[]
}
export interface AdminStatsOut {
  total_users: number
  total_families: number
  today_tasks: number
  pending_submissions: number
}
```

## 生产部署

管理后台前端构建产物放入 `admin/dist/`，由后端 Nginx 或 FastAPI static 挂载服务：

```python
# app/main.py 挂载静态文件
from fastapi.staticfiles import StaticFiles
app.mount("/admin", StaticFiles(directory="admin/dist", html=True), name="admin")
```

或通过 docker-compose 中 Nginx 反向代理 `/admin/` 到前端容器。当前阶段先做开发环境，生产部署在部署阶段完善。
