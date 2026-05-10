import { request } from './request'

export interface RegisterParams {
  phone: string
  password: string
  role: 'parent' | 'student'
}

export interface LoginParams {
  phone: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface UserOut {
  id: string
  phone: string
  role: 'parent' | 'student'
  family_id: string | null
}

export interface FamilyOut {
  id: string
  code: string
}

export function register(data: RegisterParams) {
  return request<TokenResponse>('/auth/register', 'POST', data)
}

export function login(data: LoginParams) {
  return request<TokenResponse>('/auth/login', 'POST', data)
}

export function getMe() {
  return request<UserOut>('/auth/me', 'GET')
}

export function bindFamily(code: string) {
  return request<FamilyOut>('/auth/bind', 'POST', { code })
}

export function studentBindFamily(code: string) {
  return request<FamilyOut>('/auth/student-bind', 'POST', { code })
}
