import { defineStore } from 'pinia'
import { useTasksStore } from './tasks'

export const useSyncStore = defineStore('sync', () => {
  let timer: ReturnType<typeof setInterval> | null = null
  const INTERVAL = 30000

  function start() {
    if (timer) return
    const tasksStore = useTasksStore()
    tasksStore.fetchTodayTasks()
    timer = setInterval(() => {
      tasksStore.fetchTodayTasks()
    }, INTERVAL)
  }

  function stop() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  return { start, stop }
})
