const TOKEN_KEY = 'studybuddy_token'

export function getToken(): string | null {
  return uni.getStorageSync(TOKEN_KEY) || null
}

export function setToken(token: string): void {
  uni.setStorageSync(TOKEN_KEY, token)
}

export function removeToken(): void {
  uni.removeStorageSync(TOKEN_KEY)
}

export function setCache(key: string, data: any): void {
  uni.setStorageSync(key, JSON.stringify(data))
}

export function getCache<T = any>(key: string): T | null {
  const raw = uni.getStorageSync(key)
  if (!raw) return null
  try {
    return JSON.parse(raw) as T
  } catch {
    return null
  }
}
