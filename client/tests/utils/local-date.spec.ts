import { describe, expect, it } from 'vitest'
import { addCalendarDays, formatRangeSummary, inclusiveDays, localToday } from '@/utils/local-date'

describe('local date helpers', () => {
  it('formats local calendar date without UTC conversion', () => {
    expect(localToday(new Date(2026, 6, 11, 0, 30))).toBe('2026-07-11')
  })

  it('adds calendar days across month boundaries', () => {
    expect(addCalendarDays('2026-02-27', 2)).toBe('2026-03-01')
    expect(addCalendarDays('2026-07-11', 6)).toBe('2026-07-17')
    expect(addCalendarDays('2026-07-11', 29)).toBe('2026-08-09')
  })

  it('counts inclusive days and formats summary', () => {
    expect(inclusiveDays('2026-07-11', '2026-07-17')).toBe(7)
    expect(formatRangeSummary('2026-07-11', '2026-07-17')).toContain('2026-07-11—2026-07-17')
  })
})
