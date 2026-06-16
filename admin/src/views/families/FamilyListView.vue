<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listFamilies, deleteFamily } from '@/api/families'
import type { AdminFamilyOut } from '@/types/family'
import type { PaginatedResponse } from '@/types/api'
import { message } from 'ant-design-vue'

const router = useRouter()
const loading = ref(false)
const data = ref<PaginatedResponse<AdminFamilyOut>>({ total: 0, items: [], page: 1, page_size: 20 })
const filters = reactive({ code: '' })

const columns = [
  { title: '邀请码', dataIndex: 'code' },
  { title: '成员数', dataIndex: 'member_count' },
  { title: '操作', key: 'action' },
]

async function fetchData(page = 1) {
  loading.value = true
  try {
    const res = await listFamilies({ page, page_size: 20, ...filters })
    data.value = res.data
  } finally {
    loading.value = false
  }
}

async function handleDelete(record: AdminFamilyOut) {
  await deleteFamily(record.id)
  message.success('已删除')
  fetchData(data.value.page)
}

onMounted(() => fetchData())
</script>

<template>
  <div>
    <h2 style="margin-bottom:16px">家庭管理</h2>
    <a-space style="margin-bottom:16px">
      <a-input v-model:value="filters.code" placeholder="邀请码" style="width:160px" />
      <a-button type="primary" @click="fetchData()">搜索</a-button>
    </a-space>
    <a-table :columns="columns" :data-source="data.items" :loading="loading" row-key="id"
      :pagination="{ total: data.total, pageSize: 20, onChange: fetchData }">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="router.push(`/families/${record.id}`)">详情</a-button>
            <a-popconfirm title="确定删除该家庭？" @confirm="handleDelete(record)">
              <a-button size="small" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>
  </div>
</template>
