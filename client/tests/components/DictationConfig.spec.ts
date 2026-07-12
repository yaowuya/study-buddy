import { describe, expect, it, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DictationConfig from '@/components/DictationConfig.vue'

beforeEach(() => vi.clearAllMocks())

describe('DictationConfig', () => {
  it('does not render inputs and help while disabled by the switch', () => {
    const wrapper = mount(DictationConfig, { props: { enabled: false, words: [] } })
    expect(wrapper.find('input').exists()).toBe(false)
    expect(wrapper.text()).not.toContain('我们将为每天的作业生成听写卡片')
  })

  it('trims and de-duplicates added words', async () => {
    const wrapper = mount(DictationConfig, { props: { enabled: true, words: ['Apple'] } })
    await wrapper.find('input').setValue(' apple ')
    await wrapper.find('.add-word-btn').trigger('tap')
    expect(wrapper.emitted('update:words')).toBeUndefined()
    await wrapper.find('input').setValue('banana')
    await wrapper.find('.add-word-btn').trigger('tap')
    expect(wrapper.emitted('update:words')?.at(-1)).toEqual([['Apple', 'banana']])
  })
})
