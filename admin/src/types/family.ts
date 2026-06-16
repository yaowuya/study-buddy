import type { AdminUserOut } from './user'

export interface AdminFamilyOut {
  id: string
  code: string
  member_count: number
  is_deleted: boolean
}

export interface AdminFamilyDetailOut extends AdminFamilyOut {
  members: AdminUserOut[]
}
