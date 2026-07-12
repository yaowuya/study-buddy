import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'

describe('TaskEdit', () => {
  it('uses the shared dictation configuration component', () => {
    const source = readFileSync('src/pages/parent/task-edit.vue', 'utf8')
    expect(source).toContain('<DictationConfig')
    expect(source).toContain("import DictationConfig from '@/components/DictationConfig.vue'")
    expect(source).not.toContain('<view class="dictation-card">')
  })
})
