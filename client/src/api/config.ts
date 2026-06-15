// API 配置
// H5 开发环境使用代理，App/生产环境使用完整 URL

// 生产环境 API 地址
const PROD_API_URL = 'http://106.55.249.101:8000/api/v1'

// 本地开发 API 地址（真机调试用）
const DEV_API_URL = 'http://10.10.41.184:8000/api/v1'

// #ifdef H5
// H5 端：开发环境走代理，生产环境直接请求
const BASE_URL = import.meta.env.DEV ? '/api/v1' : PROD_API_URL
// #endif

// #ifndef H5
// App 端：打包后用生产地址，调试时用本地地址
// 正式打包时 import.meta.env.DEV 为 false
const BASE_URL = import.meta.env.DEV ? DEV_API_URL : PROD_API_URL
// #endif

export { BASE_URL }
