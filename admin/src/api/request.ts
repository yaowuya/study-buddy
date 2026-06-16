import axios from 'axios'
import { message } from 'ant-design-vue'

const instance = axios.create({
  baseURL: '/api/v1/admin',
  timeout: 10000,
})

// 请求拦截：自动附加 Bearer token
instance.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：统一错误处理
instance.interceptors.response.use(
  (res) => res,
  (err) => {
    const status = err.response?.status
    if (status === 401) {
      localStorage.removeItem('admin_token')
      window.location.href = '/login'
    } else if (status === 403) {
      message.error('无权限执行此操作')
    } else if (status && status >= 500) {
      message.error('服务器错误，请稍后重试')
    } else if (!err.response) {
      message.error('网络异常，请检查网络连接')
    }
    return Promise.reject(err)
  },
)

export default instance
