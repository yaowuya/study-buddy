import { request } from './request'

export interface TaskOut {
  id: string
  type: 'school' | 'home'
  title: string
  desc: string | null
  duration: number | null
  status: 'pending' | 'in_progress' | 'submitted' | 'graded'
  date: string
  subject: string | null
  has_dictation: boolean
}

export interface TaskCreateParams {
  type: 'school' | 'home'
  title: string
  desc?: string
  duration?: number
  date: string
  subject?: string
}

export interface TaskUpdateParams {
  title?: string
  desc?: string
  duration?: number
  date?: string
  subject?: string
}

export function createTask(data: TaskCreateParams) {
  return request<TaskOut>('/tasks/', 'POST', data)
}

export function listTasks(dateFrom?: string, dateTo?: string) {
  const parts: string[] = []
  if (dateFrom) parts.push(`date_from=${dateFrom}`)
  if (dateTo) parts.push(`date_to=${dateTo}`)
  const qs = parts.join('&')
  return request<TaskOut[]>(`/tasks/${qs ? '?' + qs : ''}`, 'GET')
}

export function getTask(id: string) {
  return request<TaskOut>(`/tasks/${id}`, 'GET')
}

export function updateTask(id: string, data: TaskUpdateParams) {
  return request<TaskOut>(`/tasks/${id}`, 'PATCH', data)
}

export function updateTaskStatus(id: string, status: string) {
  return request<TaskOut>(`/tasks/${id}/status`, 'PATCH', { status })
}

export function deleteTask(id: string) {
  return request(`/tasks/${id}`, 'DELETE')
}
