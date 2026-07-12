const LEADING_DATE_HEADING = /^\s*\d{4}[.\-/年]\d{1,2}[.\-/月]\d{1,2}日?(?:周[一二三四五六日天])?\s*练习\s*[:：]?\s*$/

export function taskDescriptionLines(description: string | null | undefined): string[] {
  const lines = (description || '').split('\n').map(line => line.trim()).filter(Boolean)
  if (lines.length && LEADING_DATE_HEADING.test(lines[0])) {
    return lines.slice(1)
  }
  return lines
}
