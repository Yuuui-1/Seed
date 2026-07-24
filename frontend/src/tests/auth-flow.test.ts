import { describe, expect, it, vi } from 'vitest'
import { createRefreshCoordinator } from '@/api/refresh'
import { getGeneratedReportId } from '@/api/report'
import { resolveAuthNavigation, safeRedirect } from '@/router/guards'

describe('private route navigation', () => {
  it('redirects a guest to login with the original path', () => {
    expect(resolveAuthNavigation(false, '/report/42')).toEqual({
      name: 'login',
      query: { redirect: '/report/42' },
    })
  })

  it('allows an authenticated user to continue', () => {
    expect(resolveAuthNavigation(true, '/history')).toBe(true)
  })

  it('rejects an external redirect target', () => {
    expect(safeRedirect('https://attacker.example', '/')).toBe('/')
    expect(safeRedirect('//attacker.example', '/')).toBe('/')
    expect(safeRedirect('/assessment', '/')).toBe('/assessment')
  })
})

describe('token refresh coordination', () => {
  it('shares one refresh request across concurrent callers', async () => {
    const refresh = vi.fn().mockResolvedValue('new-token')
    const coordinator = createRefreshCoordinator(refresh)

    const results = await Promise.all([
      coordinator.refresh(),
      coordinator.refresh(),
      coordinator.refresh(),
    ])

    expect(results).toEqual(['new-token', 'new-token', 'new-token'])
    expect(refresh).toHaveBeenCalledTimes(1)
  })

  it('clears the in-flight request after a refresh failure', async () => {
    const refresh = vi.fn().mockRejectedValueOnce(new Error('expired')).mockResolvedValue('new-token')
    const coordinator = createRefreshCoordinator(refresh)

    await expect(coordinator.refresh()).rejects.toThrow('expired')
    await expect(coordinator.refresh()).resolves.toBe('new-token')
    expect(refresh).toHaveBeenCalledTimes(2)
  })
})

describe('report identifier semantics', () => {
  it('takes the report id from the generation response', () => {
    expect(getGeneratedReportId({ data: { id: 17, assessment_id: 42 } })).toBe(17)
  })
})
