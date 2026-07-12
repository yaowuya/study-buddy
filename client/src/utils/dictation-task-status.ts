import type { TaskOut } from '@/api/tasks'

export function shouldStartDictationTask(status: TaskOut['status']): boolean {
  return status === 'pending'
}
