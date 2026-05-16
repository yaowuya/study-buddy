import { request } from './request'

export interface DictationItemOut {
  id: string
  task_id: string
  content: string
  speed: number
  pause_interval: number
}

export interface DictationItemCreate {
  content: string
  speed?: number
  pause_interval?: number
}

export function createDictationItems(taskId: string, items: DictationItemCreate[]) {
  return request<DictationItemOut[]>('/dictation/', 'POST', { task_id: taskId, items })
}

export function getDictationItems(taskId: string) {
  return request<DictationItemOut[]>(`/dictation/${taskId}`, 'GET')
}

export function deleteDictationItems(taskId: string) {
  return request(`/dictation/${taskId}`, 'DELETE')
}
