import { describe, expect, it, vi } from 'vitest'
import { synchronizeHomeworkPage } from '@/utils/homework-plan-flow'

describe('synchronizeHomeworkPage', () => {
  it('materializes before fetching task and plan data', async () => {
    const order: string[] = []
    await synchronizeHomeworkPage({
      materialize: async () => { order.push('materialize') },
      fetchTasks: async () => { order.push('tasks') },
      fetchPlans: async () => { order.push('plans') },
    })
    expect(order[0]).toBe('materialize')
    expect(order.slice(1).sort()).toEqual(['plans', 'tasks'])
  })

  it('continues fetching tasks after a synchronization failure', async () => {
    const fetchTasks = vi.fn().mockResolvedValue(undefined)
    const onSyncError = vi.fn()
    await synchronizeHomeworkPage({
      materialize: vi.fn().mockRejectedValue(new Error('offline')),
      fetchTasks,
      onSyncError,
    })
    expect(onSyncError).toHaveBeenCalledOnce()
    expect(fetchTasks).toHaveBeenCalledOnce()
  })
})
