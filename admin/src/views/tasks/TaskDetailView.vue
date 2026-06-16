<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTask, deleteTask } from '@/api/tasks'
import type { AdminTaskDetailOut } from '@/types/task'
import { message } from 'ant-design-vue'
import { formatStatus } from '@/utils/format'

const route = useRoute()
const router = useRouter()
const task = ref<AdminTaskDetailOut | null>(null)

const dictationColumns = [
  { title: '内容', dataIndex: 'content' },
  { title: '语速', dataIndex: 'speed' },
  { title: '暂停(秒)', dataIndex: 'pause_interval' },
]

async function fetchTask() {
  const res = await getTask(route.params.id as string)
  task.value = res.data
}

async function handleDelete() {
  if (!task.value) return
  await deleteTask(task.value.id)
  message.success('已删除')
  router.push('/tasks')
}

onMounted(fetchTask)
</script>

<template>
  <div v-if="task">
    <a-page-header :title="`任务详情 - ${task.title}`" @back="router.back()">
      <template #extra>
        <a-popconfirm title="确定删除该任务？" @confirm="handleDelete">
          <a-button danger>删除</a-button>
        </a-popconfirm>
      </template>
    </a-page-header>

    <a-card title="基本信息" style="margin-top:16px">
      <a-descriptions :column="2" bordered>
        <a-descriptions-item label="标题">{{ task.title }}</a-descriptions-item>
        <a-descriptions-item label="类型">{{ task.type === 'school' ? '学校' : '家庭' }}</a-descriptions-item>
        <a-descriptions-item label="科目">{{ task.subject || '-' }}</a-descriptions-item>
        <a-descriptions-item label="状态">{{ formatStatus(task.status) }}</a-descriptions-item>
        <a-descriptions-item label="日期">{{ task.date }}</a-descriptions-item>
        <a-descriptions-item label="时长">{{ task.duration ? `${task.duration}分钟` : '-' }}</a-descriptions-item>
        <a-descriptions-item label="描述" :span="2">{{ task.desc || '-' }}</a-descriptions-item>
      </a-descriptions>
    </a-card>

    <a-card v-if="task.submission" title="提交信息" style="margin-top:16px">
      <a-descriptions :column="2" bordered>
        <a-descriptions-item label="批改结果">
          <a-tag :color="task.submission.is_correct === true ? 'green' : task.submission.is_correct === false ? 'red' : 'default'">
            {{ task.submission.is_correct === true ? '合格' : task.submission.is_correct === false ? '不合格' : '未批改' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="提交时间">{{ task.submission.submitted_at }}</a-descriptions-item>
        <a-descriptions-item label="评语" :span="2">{{ task.submission.comment || '-' }}</a-descriptions-item>
      </a-descriptions>
    </a-card>

    <a-card v-if="task.dictation_items?.length" title="听写条目" style="margin-top:16px">
      <a-table :columns="dictationColumns" :data-source="task.dictation_items" :pagination="false" row-key="content" />
    </a-card>
  </div>
</template>
