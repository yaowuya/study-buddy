import { describe, expect, it } from 'vitest'
import { dictationPositionLabel } from '@/utils/dictation-progress'

describe('dictationPositionLabel', () => {
  it('shows completion instead of an invalid zero position', () => {
    expect(dictationPositionLabel(-1, -1)).toBe('已完成')
  })

  it('shows the active or next word position while dictation is pending', () => {
    expect(dictationPositionLabel(1, 0)).toBe('第 2 个')
    expect(dictationPositionLabel(-1, 2)).toBe('第 3 个')
  })
})
