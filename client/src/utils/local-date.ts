function parseLocalDate(value: string): Date {
  const [year, month, day] = value.split('-').map(Number)
  return new Date(year, month - 1, day)
}

export function localToday(now = new Date()): string {
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function addCalendarDays(value: string, amount: number): string {
  const result = parseLocalDate(value)
  result.setDate(result.getDate() + amount)
  return localToday(result)
}

export function inclusiveDays(start: string, end: string): number {
  const milliseconds = parseLocalDate(end).getTime() - parseLocalDate(start).getTime()
  return Math.floor(milliseconds / 86_400_000) + 1
}

export function formatRangeSummary(start: string, end: string): string {
  return `每天一份 · ${start}—${end}`
}
