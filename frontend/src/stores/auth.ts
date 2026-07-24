import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import client from '@/api/client'

interface User {
  id: number
  email: string
  nickname: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const isAuthenticated = computed(() => !!accessToken.value)

  async function login(email: string, password: string) {
    const res = await client.post('/auth/login', { email, password })
    const { user: u, access_token, refresh_token } = res.data
    user.value = u
    accessToken.value = access_token
    refreshToken.value = refresh_token
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
  }

  async function register(email: string, password: string, nickname: string) {
    const res = await client.post('/auth/register', { email, password, nickname })
    const { user: u, access_token, refresh_token } = res.data
    user.value = u
    accessToken.value = access_token
    refreshToken.value = refresh_token
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
  }

  async function tryRefreshToken(): Promise<boolean> {
    if (!refreshToken.value) return false
    try {
      const res = await client.post('/auth/refresh', { refresh_token: refreshToken.value })
      accessToken.value = res.data.access_token
      refreshToken.value = res.data.refresh_token
      localStorage.setItem('access_token', res.data.access_token)
      localStorage.setItem('refresh_token', res.data.refresh_token)
      return true
    } catch {
      return false
    }
  }

  async function fetchMe() {
    const res = await client.get('/auth/me')
    user.value = res.data
  }

  function logout() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, accessToken, refreshToken, isAuthenticated, login, register, tryRefreshToken, fetchMe, logout }
})
