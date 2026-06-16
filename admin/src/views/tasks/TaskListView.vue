<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listTasks, deleteTask } from '@/api/tasks'
import { listFamilies } from '@/api/families'
import type { AdminTaskOut } from '@/types/task'
import type { PaginatedResponse } from '@/types/api'
import type { AdminFamilyOut } from '@/types/family'
import { message } from 'ant-design-vue'
import { formatStatus, statusColor } from '@/utils/format'
import dayjs from 'dayjs'
import type { Dayjs } from 'dayjs'

const router = useRouter()
const loading = ref(false)
const data = ref<PaginatedResponse<AdminTaskOut>>({ total: 0, items: [], page: 1, page_size: 20 })
const filters = reactive({
  task_status: undefined as string | undefined,
  family_id: undefined as string | undefined,
})
// RangePicker 绑定值：[Dayjs, Dayjs] | null
const dateRange = ref<[Dayjs, Dayjs] | null>(null)

// ── RangePicker 快捷预设 ──
const rangePresets = [
  { label: '今日', value: [dayjs(), dayjs()] as [Dayjs, Dayjs] },
  { label: '最近7天', value: [dayjs().subtract(6, 'day'), dayjs()] as [Dayjs, Dayjs] },
  { label: '最近30天', value: [dayjs().subtract(29, 'day'), dayjs()] as [Dayjs, Dayjs] },
  { label: '本周', value: [dayjs().startOf('week'), dayjs().endOf('week')] as [Dayjs, Dayjs] },
  { label: '本月', value: [dayjs().startOf('month'), dayjs().endOf('month')] as [Dayjs, Dayjs] },
  { label: '今年', value: [dayjs().startOf('year'), dayjs().endOf('year')] as [Dayjs, Dayjs] },
]

function onRangeChange(val: [Dayjs, Dayjs] | null) {
  dateRange.value = val
  fetchData()
}

// ── 家庭下拉 ──
const familyOptions = ref<{ value: string; label: string }[]>([])
const familySearching = ref(false)

async function searchFamilies(keyword: string) {
  familySearching.value = true
  try {
    const res = await listFamilies({ code: keyword, page_size: 50 })
    familyOptions.value = res.data.items.map((f: AdminFamilyOut) => ({
      value: f.id,
      label: `邀请码 ${f.code}（${f.member_count} 人）`,
    }))
  } finally {
    familySearching.value = false
  }
}

onMounted(() => {
  searchFamilies('')
  fetchData()
})

// ── 表格 ──
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
    if (filters.family_id) params.family_id = filters.family_id
    if (dateRange.value) {
      params.date_from = dateRange.value[0].format('YYYY-MM-DD')
      params.date_to = dateRange.value[1].format('YYYY-MM-DD')
    }
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
</script>

<template>
  <div>
    <h2 style="margin-bottom:16px">作业管理</h2>

    <a-space style="margin-bottom:16px" wrap>
      <!-- 家庭下拉 -->
      <a-select
        v-model:value="filters.family_id"
        placeholder="全部家庭"
        allowClear
        show-search
        :filter-option="false"
        :loading="familySearching"
        style="width:220px"
        @search="searchFamilies"
        @change="fetchData()"
      >
        <a-select-option v-for="opt in familyOptions" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </a-select-option>
      </a-select>

      <!-- 状态 -->
      <a-select
        v-model:value="filters.task_status"
        placeholder="全部状态"
        allowClear
        style="width:130px"
        @change="fetchData()"
      >
        <a-select-option value="pending">未开始</a-select-option>
        <a-select-option value="in_progress">进行中</a-select-option>
        <a-select-option value="submitted">已提交</a-select-option>
        <a-select-option value="graded">已批改</a-select-option>
      </a-select>

      <!-- 日期范围选择器（内含快捷预设） -->
      <a-range-picker
        v-model:value="dateRange"
        :presets="rangePresets"
        style="width:280px"
        @change="onRangeChange"
      />

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
