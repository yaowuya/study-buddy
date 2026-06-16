export interface AdminUserOut {
  id: string
  phone: string
  role: 'parent' | 'student'
  family_id: string | null
  is_active: boolean
  is_deleted: boolean
}

export interface AdminUserDetailOut extends AdminUserOut {
  family_code: string | null
  task_count: number
}

export interface AdminUserUpdate {
  role?: string
  is_active?: boolean
}
