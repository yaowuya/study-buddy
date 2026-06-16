<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listTasks, deleteTask } from '@/api/tasks'
import type { AdminTaskOut } from '@/types/task'
import type { PaginatedResponse } from '@/types/api'
import { message } from 'ant-design-vue'
import { formatStatus, statusColor } from '@/utils/format'

const router = useRouter()
const loading = ref(false)
const data = ref<PaginatedResponse<AdminTaskOut>>({ total: 0, items: [], page: 1, page_size: 20 })
const filters = reactive({ task_status: undefined as string | undefined, date_from: '', date_to: '' })

const columns = [
  { title: '标题', dataIndex: 'title' },
  { title: '类型', dataIndex: 'type', key: 'type' },
  { title: '科目', dataIndex: 'subject' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '日期', dataIndex: 'date' },
  { title: '操作', key: 'action' },
]

async function fetchData(page = 1) {
  loading.value = true
  try {
    const params: Record<string, any> = { page, page_size: 20 }
    if (filters.task_status) params.task_status = filters.task_status
    if (filters.date_from) params.date_from = filters.date_from
    if (filters.date_to) params.date_to = filters.date_to
    const res = await listTasks(params)
    data.value = res.data
  } finally {
    loading.value = false
  }
}

async function handleDelete(record: AdminTaskOut) {
  await deleteTask(record.id)
  message.success('已删除')
  fetchData(data.value.page)
}

onMounted(() => fetchData())
</script>

<template>
  <div>
    <h2 style="margin-bottom:16px">作业管理</h2>
    <a-space style="margin-bottom:16px" wrap>
      <a-select v-model:value="filters.task_status" placeholder="全部状态" allowClear style="width:140px">
        <a-select-option value="pending">未开始</a-select-option>
        <a-select-option value="in_progress">进行中</a-select-option>
        <a-select-option value="submitted">已提交</a-select-option>
        <a-select-option value="graded">已批改</a-select-option>
      </a-select>
      <a-input v-model:value="filters.date_from" type="date" style="width:150px" />
      <span>至</span>
      <a-input v-model:value="filters.date_to" type="date" style="width:150px" />
      <a-button type="primary" @click="fetchData()">搜索</a-button>
    </a-space>
    <a-table :columns="columns" :data-source="data.items" :loading="loading" row-key="id"
      :pagination="{ total: data.total, pageSize: 20, onChange: fetchData }">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'type'">{{ record.type === 'school' ? '学校' : '家庭' }}</template>
        <template v-else-if="column.key === 'status'">
          <a-tag :color="statusColor(record.status)">{{ formatStatus(record.status) }}</a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="router.push(`/tasks/${record.id}`)">详情</a-button>
            <a-popconfirm title="确定删除该任务？" @confirm="handleDelete(record)">
              <a-button size="small" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>
  </div>
</template>
