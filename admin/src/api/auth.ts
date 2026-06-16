import request from './request'
import type { TokenResponse, AdminOut, AdminPasswordChange } from '@/types/auth'

export function login(username: string, password: string) {
  return request.post<TokenResponse>('/auth/login', { username, password })
}

export function getMe() {
  return request.get<AdminOut>('/auth/me')
}

export function changePassword(data: AdminPasswordChange) {
  return request.patch('/auth/password', data)
}
