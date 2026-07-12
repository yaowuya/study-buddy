import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import HomeworkPlanCard from '@/components/HomeworkPlanCard.vue'

const plan = {
  id: 'p1', type: 'home', title: '每日朗读', desc: '朗读两遍', duration: 20, subject: '语文',
  start_date: '2026-07-11', end_date: '2026-07-17', status: 'active', has_dictation: true,
  dictation_count: 3, total_days: 7, generated_count: 1, remaining_days: 6,
  days_until_start: null, today_generated: true, updated_at: '2026-07-11T00:00:00Z',
} as const

describe('HomeworkPlanCard', () => {
  it('renders status, progress metadata and emits actions', async () => {
    const wrapper = mount(HomeworkPlanCard, { props: { plan: plan as any } })
    expect(wrapper.text()).toContain('进行中')
    expect(wrapper.text()).toContain('已生成 1 / 7 份')
    expect(wrapper.text()).toContain('听写 · 3 个词')
    await wrapper.find('.edit-btn').trigger('tap')
    await wrapper.find('.delete-btn').trigger('tap')
    expect(wrapper.emitted('edit')).toEqual([['p1']])
    expect(wrapper.emitted('delete')).toEqual([['p1']])
  })
})
