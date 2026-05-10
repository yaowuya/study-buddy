import { request } from './request'

export interface MistakeOut {
  id: string
  task_id: string
  subject: string | null
  archived: boolean
}

export function listMistakes(subject?: string, archived?: boolean) {
  const params = new URLSearchParams()
  if (subject) params.set('subject', subject)
  if (archived !== undefined) params.set('archived', String(archived))
  const qs = params.toString()
  return request<MistakeOut[]>(`/mistakes/${qs ? '?' + qs : ''}`, 'GET')
}

export function archiveMistake(id: string) {
  return request<MistakeOut>(`/mistakes/${id}/archive`, 'POST')
}
