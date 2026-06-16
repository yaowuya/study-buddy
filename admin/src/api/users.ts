import request from './request'
import type { AdminUserOut, AdminUserDetailOut, AdminUserUpdate } from '@/types/user'
import type { PaginatedResponse } from '@/types/api'

export function listUsers(params?: {
  page?: number
  page_size?: number
  phone?: string
  role?: string
  is_active?: boolean
}) {
  return request.get<PaginatedResponse<AdminUserOut>>('/users/', { params })
}

export function getUser(id: string) {
  return request.get<AdminUserDetailOut>(`/users/${id}`)
}

export function updateUser(id: string, data: AdminUserUpdate) {
  return request.patch<AdminUserOut>(`/users/${id}`, data)
}

export function deleteUser(id: string) {
  return request.delete(`/users/${id}`)
}
