import request from './request'
import type { AdminFamilyOut, AdminFamilyDetailOut } from '@/types/family'
import type { PaginatedResponse } from '@/types/api'

export function listFamilies(params?: { page?: number; page_size?: number; code?: string }) {
  return request.get<PaginatedResponse<AdminFamilyOut>>('/families/', { params })
}

export function getFamily(id: string) {
  return request.get<AdminFamilyDetailOut>(`/families/${id}`)
}

export function deleteFamily(id: string) {
  return request.delete(`/families/${id}`)
}
