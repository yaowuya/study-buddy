<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getFamily, deleteFamily } from '@/api/families'
import type { AdminFamilyDetailOut } from '@/types/family'
import { message } from 'ant-design-vue'

const route = useRoute()
const router = useRouter()
const family = ref<AdminFamilyDetailOut | null>(null)

const memberColumns = [
  { title: '手机号', dataIndex: 'phone' },
  { title: '角色', dataIndex: 'role', key: 'role' },
  { title: '状态', dataIndex: 'is_active', key: 'is_active' },
]

async function fetchFamily() {
  const res = await getFamily(route.params.id as string)
  family.value = res.data
}

async function handleDelete() {
  if (!family.value) return
  await deleteFamily(family.value.id)
  message.success('已删除')
  router.push('/families')
}

onMounted(fetchFamily)
</script>

<template>
  <div v-if="family">
    <a-page-header :title="`家庭详情 - ${family.code}`" @back="router.back()" />
    <a-row :gutter="16" style="margin-top:16px">
      <a-col :span="8">
        <a-card title="基本信息">
          <a-descriptions :column="1" bordered>
            <a-descriptions-item label="邀请码">{{ family.code }}</a-descriptions-item>
            <a-descriptions-item label="成员数">{{ family.member_count }}</a-descriptions-item>
          </a-descriptions>
          <a-popconfirm title="确定删除该家庭？" @confirm="handleDelete" style="margin-top:16px;display:block">
            <a-button danger style="margin-top:16px">删除家庭</a-button>
          </a-popconfirm>
        </a-card>
      </a-col>
      <a-col :span="16">
        <a-card title="成员列表">
          <a-table :columns="memberColumns" :data-source="family.members" row-key="id" :pagination="false">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'role'">
                <a-tag :color="record.role === 'parent' ? 'blue' : 'green'">
                  {{ record.role === 'parent' ? '家长' : '学生' }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'is_active'">
                <a-badge :status="record.is_active ? 'success' : 'error'" :text="record.is_active ? '启用' : '禁用'" />
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>
