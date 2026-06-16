// API 配置
// H5 开发环境使用代理，App/生产环境使用完整 URL

// 生产环境 API 地址
const PROD_API_URL = 'http://106.55.249.101:8000/api/v1'

// 本地开发 API 地址（真机调试用）
const DEV_API_URL = 'http://10.10.41.184:8000/api/v1'

// 判断当前运行环境
// typeof window 在 H5 下存在，App 下不存在
function getBaseUrl(): string {
  // H5 开发环境走 Vite 代理
  if (import.meta.env.DEV && typeof window !== 'undefined') {
    return '/api/v1'
  }
  // App 开发真机调试走内网
  if (import.meta.env.DEV) {
    return DEV_API_URL
  }
  // 生产环境
  return PROD_API_URL
}

export const BASE_URL = getBaseUrl()
