<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listUsers, updateUser, deleteUser } from '@/api/users'
import type { AdminUserOut } from '@/types/user'
import type { PaginatedResponse } from '@/types/api'
import { message } from 'ant-design-vue'

const router = useRouter()
const loading = ref(false)
const data = ref<PaginatedResponse<AdminUserOut>>({ total: 0, items: [], page: 1, page_size: 20 })
const filters = reactive({ phone: '', role: undefined as string | undefined, is_active: undefined as boolean | undefined })

const columns = [
  { title: '手机号', dataIndex: 'phone' },
  { title: '角色', dataIndex: 'role', key: 'role' },
  { title: '状态', dataIndex: 'is_active', key: 'is_active' },
  { title: '操作', key: 'action' },
]

async function fetchData(page = 1) {
  loading.value = true
  try {
    const res = await listUsers({ page, page_size: 20, ...filters })
    data.value = res.data
  } finally {
    loading.value = false
  }
}

async function toggleActive(record: AdminUserOut) {
  await updateUser(record.id, { is_active: !record.is_active })
  message.success(record.is_active ? '已禁用' : '已启用')
  fetchData(data.value.page)
}

async function handleDelete(record: AdminUserOut) {
  await deleteUser(record.id)
  message.success('已删除')
  fetchData(data.value.page)
}

onMounted(() => fetchData())
</script>

<template>
  <div>
    <h2 style="margin-bottom:16px">用户管理</h2>
    <a-space style="margin-bottom:16px">
      <a-input v-model:value="filters.phone" placeholder="手机号" style="width:200px" />
      <a-select v-model:value="filters.role" placeholder="全部角色" allowClear style="width:120px">
        <a-select-option value="parent">家长</a-select-option>
        <a-select-option value="student">学生</a-select-option>
      </a-select>
      <a-select v-model:value="filters.is_active" placeholder="全部状态" allowClear style="width:120px">
        <a-select-option :value="true">启用</a-select-option>
        <a-select-option :value="false">禁用</a-select-option>
      </a-select>
      <a-button type="primary" @click="fetchData()">搜索</a-button>
    </a-space>

    <a-table
      :columns="columns"
      :data-source="data.items"
      :loading="loading"
      row-key="id"
      :pagination="{ total: data.total, pageSize: 20, onChange: fetchData }"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'role'">
          <a-tag :color="record.role === 'parent' ? 'blue' : 'green'">
            {{ record.role === 'parent' ? '家长' : '学生' }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'is_active'">
          <a-badge :status="record.is_active ? 'success' : 'error'" :text="record.is_active ? '启用' : '禁用'" />
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="router.push(`/users/${record.id}`)">详情</a-button>
            <a-popconfirm :title="record.is_active ? '确定禁用该用户？' : '确定启用该用户？'" @confirm="toggleActive(record)">
              <a-button size="small" :type="record.is_active ? 'default' : 'primary'">
                {{ record.is_active ? '禁用' : '启用' }}
              </a-button>
            </a-popconfirm>
            <a-popconfirm title="确定删除该用户？" @confirm="handleDelete(record)">
              <a-button size="small" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>
  </div>
</template>
