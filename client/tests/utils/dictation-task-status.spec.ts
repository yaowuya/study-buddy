import { describe, expect, it } from 'vitest'
import { shouldStartDictationTask } from '@/utils/dictation-task-status'

describe('shouldStartDictationTask', () => {
  it('only moves pending tasks into progress', () => {
    expect(shouldStartDictationTask('pending')).toBe(true)
    expect(shouldStartDictationTask('in_progress')).toBe(false)
    expect(shouldStartDictationTask('submitted')).toBe(false)
    expect(shouldStartDictationTask('graded')).toBe(false)
  })
})
