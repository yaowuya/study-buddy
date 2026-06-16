export function formatStatus(status: string): string {
  const map: Record<string, string> = {
    pending: '未开始',
    in_progress: '进行中',
    submitted: '已提交',
    graded: '已批改',
  }
  return map[status] || status
}

export function statusColor(status: string): string {
  const map: Record<string, string> = {
    pending: 'default',
    in_progress: 'blue',
    submitted: 'orange',
    graded: 'green',
  }
  return map[status] || 'default'
}
