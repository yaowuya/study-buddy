export interface AdminOut {
  id: string
  username: string
  is_active: boolean
  created_at: string
}

export interface AdminLogin {
  username: string
  password: string
}

export interface AdminPasswordChange {
  old_password: string
  new_password: string
}

export interface TokenResponse {
  access_token: string
}
