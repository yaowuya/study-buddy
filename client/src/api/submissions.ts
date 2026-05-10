import { request } from './request'

export interface SubmissionOut {
  id: string
  task_id: string
  comment: string | null
  is_correct: boolean | null
  submitted_at: string
}

export function listSubmissions(taskId?: string) {
  const qs = taskId ? `?task_id=${taskId}` : ''
  return request<SubmissionOut[]>(`/submissions/${qs}`, 'GET')
}

export function submitTask(taskId: string) {
  return request<SubmissionOut>('/submissions/', 'POST', { task_id: taskId })
}

export function gradeSubmission(submissionId: string, isCorrect: boolean, comment?: string) {
  return request<SubmissionOut>(`/submissions/${submissionId}/grade`, 'POST', { is_correct: isCorrect, comment })
}
