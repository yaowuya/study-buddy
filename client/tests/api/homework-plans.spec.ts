import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as plans from '@/api/homework-plans'
import { request } from '@/api/request'

vi.mock('@/api/request', () => ({ request: vi.fn() }))

const mockedRequest = vi.mocked(request)

describe('homework plans api', () => {
  beforeEach(() => mockedRequest.mockReset())

  it('maps all plan operations to the backend contract', async () => {
    mockedRequest.mockResolvedValue({})
    const create = { type: 'home' as const, title: '阅读', range_type: 'week' as const, dictation_items: [] }
    await plans.createHomeworkPlan(create)
    await plans.listActiveHomeworkPlans()
    await plans.getHomeworkPlan('a/b')
    const update = { type: 'home' as const, title: '阅读', start_date: '2026-07-11', end_date: '2026-07-17', updated_at: 'token', dictation_items: [] }
    await plans.updateHomeworkPlan('id', update)
    await plans.deleteHomeworkPlan('id')
    await plans.materializeHomeworkPlans()

    expect(mockedRequest.mock.calls).toEqual([
      ['/homework-plans/', 'POST', create],
      ['/homework-plans/', 'GET'],
      ['/homework-plans/a%2Fb', 'GET'],
      ['/homework-plans/id', 'PATCH', update],
      ['/homework-plans/id', 'DELETE'],
      ['/homework-plans/materialize', 'POST'],
    ])
    expect(JSON.stringify(create)).not.toContain('family_id')
  })
})
