export function dictationPositionLabel(currentIndex: number, nextUnplayedIndex: number): string {
  const index = currentIndex >= 0 ? currentIndex : nextUnplayedIndex
  return index >= 0 ? `第 ${index + 1} 个` : '已完成'
}
