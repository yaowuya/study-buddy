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
  updated_at: string | null
}

export interface TaskCreateParams {
  type: 'school' | 'home'
  title: string
  desc?: string
  duration?: number
  date: string
  subject?: string
}

export function createTask(data: TaskCreateParams) {
  return request<TaskOut>('/tasks/', 'POST', data)
}

export function listTasks(date: string) {
  return request<TaskOut[]>(`/tasks/?task_date=${date}`, 'GET')
}

export function getTask(id: string) {
  return request<TaskOut>(`/tasks/${id}`, 'GET')
}

export function updateTaskStatus(id: string, status: string) {
  return request<TaskOut>(`/tasks/${id}/status`, 'PATCH', { status })
}

export function deleteTask(id: string) {
  return request(`/tasks/${id}`, 'DELETE')
}
