import axios from 'axios'

export interface TokenPair {
  access_token: string
  refresh_token: string
}

const refreshClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

export function createRefreshCoordinator<T>(operation: () => Promise<T>) {
  let inFlight: Promise<T> | null = null

  return {
    refresh(): Promise<T> {
      if (!inFlight) {
        inFlight = operation().finally(() => {
          inFlight = null
        })
      }
      return inFlight
    },
  }
}

export async function requestTokenRefresh(refreshToken: string): Promise<TokenPair> {
  const response = await refreshClient.post('/auth/refresh', {
    refresh_token: refreshToken,
  })
  return response.data.data
}
