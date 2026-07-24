import type { RouteLocationRaw } from 'vue-router'

export function resolveAuthNavigation(
  authenticated: boolean,
  fullPath: string,
): true | RouteLocationRaw {
  if (authenticated) return true
  return {
    name: 'login',
    query: { redirect: fullPath },
  }
}

export function safeRedirect(value: unknown, fallback = '/'): string {
  if (typeof value !== 'string') return fallback
  if (!value.startsWith('/') || value.startsWith('//')) return fallback
  return value
}
