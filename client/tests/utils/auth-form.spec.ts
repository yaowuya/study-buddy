import { describe, expect, it, vi } from 'vitest'
import { authenticateFromForm } from '@/utils/auth-form'

describe('authenticateFromForm', () => {
  it('registers directly in register mode without attempting login first', async () => {
    const login = vi.fn()
    const register = vi.fn().mockResolvedValue(undefined)

    await authenticateFromForm(true, '13800000000', 'secret', 'student', { login, register })

    expect(login).not.toHaveBeenCalled()
    expect(register).toHaveBeenCalledWith('13800000000', 'secret', 'student')
  })

  it('logs in directly in login mode', async () => {
    const login = vi.fn().mockResolvedValue(undefined)
    const register = vi.fn()

    await authenticateFromForm(false, '13900000000', 'secret', 'parent', { login, register })

    expect(login).toHaveBeenCalledWith('13900000000', 'secret')
    expect(register).not.toHaveBeenCalled()
  })
})
