import { describe, expect, it } from 'vitest'
import { taskDescriptionLines } from '@/utils/task-description'

describe('taskDescriptionLines', () => {
  it('removes a leading date heading that duplicates the task card date', () => {
    expect(taskDescriptionLines('2026.07.02周四练习:\n1.准备考试用具\n2.复习错题')).toEqual([
      '1.准备考试用具',
      '2.复习错题',
    ])
  })

  it('keeps ordinary description lines unchanged', () => {
    expect(taskDescriptionLines('朗读课文\n完成练习')).toEqual(['朗读课文', '完成练习'])
  })
})
