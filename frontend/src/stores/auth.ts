import { create } from 'zustand'

type Role = 'Admin' | 'Reviewer' | 'Operator'

interface AuthState {
  token: string | null
  role: Role | null
  setAuth: (token: string, role: Role) => void
  clear: () => void
}

const STORAGE_KEY = 'auth_state'

function loadInitial(): Pick<AuthState, 'token' | 'role'> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { token: null, role: null }
    const parsed = JSON.parse(raw)
    return { token: parsed.token ?? null, role: parsed.role ?? null }
  } catch { return { token: null, role: null } }
}

export const useAuthStore = create<AuthState>((set) => {
  const init = loadInitial()
  return {
    token: init.token,
    role: init.role,
    setAuth: (token, role) => {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ token, role }))
      set({ token, role })
    },
    clear: () => {
      localStorage.removeItem(STORAGE_KEY)
      set({ token: null, role: null })
    }
  }
})

export type { Role }
