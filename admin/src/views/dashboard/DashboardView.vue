<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getStats } from '@/api/tasks'
import type { AdminStatsOut } from '@/types/task'

const stats = ref<AdminStatsOut | null>(null)

onMounted(async () => {
  const res = await getStats()
  stats.value = res.data
})
</script>

<template>
  <div>
    <h2 style="margin-bottom:24px">仪表盘</h2>
    <a-row :gutter="16">
      <a-col :span="6">
        <a-card>
          <a-statistic title="总用户数" :value="stats?.total_users ?? '-'" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="总家庭数" :value="stats?.total_families ?? '-'" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="今日作业" :value="stats?.today_tasks ?? '-'" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="待批改" :value="stats?.pending_submissions ?? '-'" value-style="color:#cf1322" />
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>
