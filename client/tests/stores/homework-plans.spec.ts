import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const api = vi.hoisted(() => ({
  listActiveHomeworkPlans: vi.fn(), getHomeworkPlan: vi.fn(), createHomeworkPlan: vi.fn(),
  updateHomeworkPlan: vi.fn(), deleteHomeworkPlan: vi.fn(), materializeHomeworkPlans: vi.fn(),
}))
vi.mock('@/api/homework-plans', () => api)

import { useHomeworkPlansStore } from '@/stores/homework-plans'

beforeEach(() => { setActivePinia(createPinia()); vi.clearAllMocks() })

describe('homework plans store', () => {
  it('deduplicates concurrent synchronization and records partial warnings', async () => {
    let resolve!: (value: any) => void
    api.materializeHomeworkPlans.mockReturnValue(new Promise(r => { resolve = r }))
    const store = useHomeworkPlansStore()
    const one = store.materialize(); const two = store.materialize()
    expect(api.materializeHomeworkPlans).toHaveBeenCalledTimes(1)
    resolve({ created_count: 0, success_count: 0, failed_count: 1, plans: [] })
    await Promise.all([one, two])
    expect(store.syncWarning).toContain('部分计划')
    expect(store.syncing).toBe(false)
  })

  it('updates and removes active list entries', async () => {
    const store = useHomeworkPlansStore()
    store.activePlans = [{ id: 'p1', title: 'old' } as any]
    api.updateHomeworkPlan.mockResolvedValue({ id: 'p1', title: 'new' })
    await store.updatePlan('p1', {} as any)
    expect(store.activePlans[0].title).toBe('new')
    api.deleteHomeworkPlan.mockResolvedValue({ ok: true })
    await store.deletePlan('p1')
    expect(store.activePlans).toEqual([])
  })
})
