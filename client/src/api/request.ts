import { getToken, removeToken } from '@/utils/storage'
import { BASE_URL } from './config'

export function request<T = any>(
  url: string,
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' = 'GET',
  data?: any,
): Promise<T> {
  return new Promise((resolve, reject) => {
    const token = getToken()
    const header: Record<string, string> = {
      'Content-Type': 'application/json',
    }
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }

    const fullUrl = `${BASE_URL}${url}`
    console.log('[request]', method, fullUrl)
    uni.request({
      url: fullUrl,
      method: method as any,
      data,
      header,
      success: (res) => {
        if (res.statusCode === 401) {
          removeToken()
          uni.reLaunch({ url: '/pages/auth/login' })
          reject(new Error('Unauthorized'))
          return
        }
        if (res.statusCode >= 400) {
          const msg = (res.data as any)?.detail || `HTTP ${res.statusCode}`
          reject(new Error(msg))
          return
        }
        resolve(res.data as T)
      },
      fail: (err) => {
        console.error('[request] fail:', method, url, err.errMsg)
        reject(new Error(err.errMsg))
      },
    })
  })
}
