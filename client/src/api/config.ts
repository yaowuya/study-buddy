// API 配置
// H5 开发环境使用代理，App/生产环境使用完整 URL

// 生产环境 API 地址（App 打包使用）
const PROD_API_URL = 'http://106.55.249.101:8000/api/v1'

// #ifdef H5
// H5 端：开发环境走代理，生产环境直接请求
const BASE_URL = import.meta.env.DEV ? '/api/v1' : PROD_API_URL
// #endif

// #ifndef H5
// App 端：直接请求生产环境 API
const BASE_URL = PROD_API_URL
// #endif

export { BASE_URL }
