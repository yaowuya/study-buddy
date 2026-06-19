import { request } from './request'

export interface MistakeOut {
  id: string
  task_id: string
  subject: string | null
  archived: boolean
}

export function listMistakes(subject?: string, archived?: boolean) {
  const parts: string[] = []
  if (subject) parts.push(`subject=${subject}`)
  if (archived !== undefined) parts.push(`archived=${archived}`)
  const qs = parts.join('&')
  return request<MistakeOut[]>(`/mistakes/${qs ? '?' + qs : ''}`, 'GET')
}

export function archiveMistake(id: string) {
  return request<MistakeOut>(`/mistakes/${id}/archive`, 'POST')
}
