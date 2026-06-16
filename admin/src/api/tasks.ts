import request from './request'
import type { AdminTaskOut, AdminTaskDetailOut, AdminStatsOut } from '@/types/task'
import type { PaginatedResponse } from '@/types/api'

export function getStats() {
  return request.get<AdminStatsOut>('/tasks/stats')
}

export function listTasks(params?: {
  page?: number
  page_size?: number
  family_id?: string
  task_status?: string
  date_from?: string
  date_to?: string
}) {
  return request.get<PaginatedResponse<AdminTaskOut>>('/tasks/', { params })
}

export function getTask(id: string) {
  return request.get<AdminTaskDetailOut>(`/tasks/${id}`)
}

export function deleteTask(id: string) {
  return request.delete(`/tasks/${id}`)
}
