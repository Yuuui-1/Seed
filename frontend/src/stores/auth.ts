import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import client from '@/api/client'
import { createRefreshCoordinator, requestTokenRefresh } from '@/api/refresh'

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

  function persistTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  async function login(email: string, password: string) {
    const res = await client.post('/auth/login', { email, password })
    const { user: u, access_token, refresh_token } = res.data
    user.value = u
    persistTokens(access_token, refresh_token)
  }

  async function register(email: string, password: string, nickname: string) {
    const res = await client.post('/auth/register', { email, password, nickname })
    const { user: u, access_token, refresh_token } = res.data
    user.value = u
    persistTokens(access_token, refresh_token)
  }

  const refreshCoordinator = createRefreshCoordinator(async () => {
    if (!refreshToken.value) throw new Error('No refresh token')
    const tokens = await requestTokenRefresh(refreshToken.value)
    persistTokens(tokens.access_token, tokens.refresh_token)
    return tokens.access_token
  })

  async function tryRefreshToken(): Promise<boolean> {
    try {
      await refreshCoordinator.refresh()
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
