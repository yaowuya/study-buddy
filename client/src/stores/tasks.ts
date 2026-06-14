import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as tasksApi from '@/api/tasks'
import type { TaskOut } from '@/api/tasks'
import { setCache, getCache } from '@/utils/storage'

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref<TaskOut[]>([])
  const loading = ref(false)

    async function fetchAllTasks(dateFrom?: string, dateTo?: string) {
    loading.value = true
    try {
      tasks.value = await tasksApi.listTasks(dateFrom, dateTo)
    } finally {
      loading.value = false
    }
  }

  async function fetchTodayTasks() {
    loading.value = true
    try {
      const today = new Date().toISOString().slice(0, 10)
      tasks.value = await tasksApi.listTasks(today, today)
      setCache('today_tasks', tasks.value)
    } finally {
      loading.value = false
    }
  }

  async function updateStatus(taskId: string, status: string) {
    const updated = await tasksApi.updateTaskStatus(taskId, status)
    const idx = tasks.value.findIndex(t => t.id === taskId)
    if (idx !== -1) tasks.value[idx] = updated
    setCache('today_tasks', tasks.value)
    return updated
  }

  async function submitTask(taskId: string) {
    const { submitTask: apiSubmit } = await import('@/api/submissions')
    await apiSubmit(taskId)
    return updateStatus(taskId, 'submitted')
  }

  function loadCached() {
    const cached = getCache<TaskOut[]>('today_tasks')
    if (Array.isArray(cached)) tasks.value = cached
  }

  const pendingTasks = () => tasks.value.filter(t => t.status === 'pending')
  const allCompleted = () => tasks.value.length > 0 && tasks.value.every(t => t.status === 'submitted' || t.status === 'graded')

  return { tasks, loading, fetchTodayTasks, fetchAllTasks, updateStatus, submitTask, loadCached, pendingTasks, allCompleted }
})
