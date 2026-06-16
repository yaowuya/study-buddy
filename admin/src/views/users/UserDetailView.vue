<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getUser, updateUser, deleteUser } from '@/api/users'
import type { AdminUserDetailOut } from '@/types/user'
import { message } from 'ant-design-vue'

const route = useRoute()
const router = useRouter()
const user = ref<AdminUserDetailOut | null>(null)

async function fetchUser() {
  const res = await getUser(route.params.id as string)
  user.value = res.data
}

async function toggleActive() {
  if (!user.value) return
  await updateUser(user.value.id, { is_active: !user.value.is_active })
  message.success(user.value.is_active ? '已禁用' : '已启用')
  fetchUser()
}

async function handleDelete() {
  if (!user.value) return
  await deleteUser(user.value.id)
  message.success('已删除')
  router.push('/users')
}

onMounted(fetchUser)
</script>

<template>
  <div v-if="user">
    <a-page-header title="用户详情" :sub-title="user.phone" @back="router.back()" />
    <a-row :gutter="16" style="margin-top:16px">
      <a-col :span="12">
        <a-card title="基本信息">
          <a-descriptions :column="1" bordered>
            <a-descriptions-item label="手机号">{{ user.phone }}</a-descriptions-item>
            <a-descriptions-item label="角色">
              <a-tag :color="user.role === 'parent' ? 'blue' : 'green'">
                {{ user.role === 'parent' ? '家长' : '学生' }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="状态">
              <a-badge :status="user.is_active ? 'success' : 'error'" :text="user.is_active ? '启用' : '禁用'" />
            </a-descriptions-item>
            <a-descriptions-item label="所属家庭">{{ user.family_code || '未绑定' }}</a-descriptions-item>
            <a-descriptions-item label="任务数">{{ user.task_count }}</a-descriptions-item>
          </a-descriptions>
          <a-space style="margin-top:16px">
            <a-popconfirm :title="user.is_active ? '确定禁用？' : '确定启用？'" @confirm="toggleActive">
              <a-button :type="user.is_active ? 'default' : 'primary'">
                {{ user.is_active ? '禁用' : '启用' }}
              </a-button>
            </a-popconfirm>
            <a-popconfirm title="确定删除？" @confirm="handleDelete">
              <a-button danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>
