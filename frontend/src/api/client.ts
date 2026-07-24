import axios from 'axios'
import type { InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/stores/auth'

interface RetryableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean
}

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (res) => res.data,
  async (error) => {
    const config = error.config as RetryableRequestConfig | undefined
    if (error.response?.status === 401 && config && !config._retry) {
      config._retry = true
      const authStore = useAuthStore()
      const refreshed = await authStore.tryRefreshToken()
      if (refreshed) {
        return client(config)
      }
      authStore.logout()
      const redirect = `${window.location.pathname}${window.location.search}`
      window.location.assign(`/login?redirect=${encodeURIComponent(redirect)}`)
    }
    return Promise.reject(error)
  }
)

export default client
