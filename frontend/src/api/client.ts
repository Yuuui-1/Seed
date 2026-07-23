import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

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
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      const refreshed = await authStore.tryRefreshToken()
      if (refreshed) {
        return client(error.config!)
      }
      authStore.logout()
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

export default client
