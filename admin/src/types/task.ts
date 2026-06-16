export interface AdminTaskOut {
  id: string
  family_id: string
  type: 'school' | 'home'
  title: string
  desc: string | null
  status: 'pending' | 'in_progress' | 'submitted' | 'graded'
  date: string
  subject: string | null
  is_deleted: boolean
}

export interface AdminTaskDetailOut extends AdminTaskOut {
  desc: string | null
  duration: number | null
  submission: {
    is_correct: boolean | null
    comment: string | null
    submitted_at: string
  } | null
  dictation_items: {
    content: string
    speed: number
    pause_interval: number
  }[]
}

export interface AdminStatsOut {
  total_users: number
  total_families: number
  today_tasks: number
  pending_submissions: number
}
