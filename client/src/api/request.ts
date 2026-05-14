import { getToken, removeToken } from '@/utils/storage'

declare const plus: any

const isApp = typeof plus !== 'undefined'
const BASE_URL = isApp
  ? 'http://10.10.41.184:8000/api/v1'
  : '/api/v1'

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

    uni.request({
      url: `${BASE_URL}${url}`,
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
        reject(new Error(err.errMsg))
      },
    })
  })
}
