import { create } from 'zustand'

type Role = 'Admin' | 'Reviewer' | 'Operator'

interface AuthState {
  token: string | null
  role: Role | null
  userId: number | null
  setAuth: (token: string | null, role: Role | null) => void
  setUser: (userId: number | null) => void
  clear: () => void
}

const STORAGE_KEY = 'auth_state'

function loadInitial(): Pick<AuthState, 'token' | 'role' | 'userId'> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { token: null, role: null, userId: null }
    const parsed = JSON.parse(raw)
    return { token: parsed.token ?? null, role: parsed.role ?? null, userId: parsed.userId ?? null }
  } catch { return { token: null, role: null, userId: null } }
}

export const useAuthStore = create<AuthState>((set, get) => {
  const init = loadInitial()
  return {
    token: init.token,
    role: init.role,
    userId: init.userId,
    setAuth: (token, role) => {
      const current = get()
      const userId = current.userId
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ token, role, userId }))
      set({ token, role })
    },
    setUser: (userId) => {
      const current = get()
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ token: current.token, role: current.role, userId }))
      set({ userId })
    },
    clear: () => {
      localStorage.removeItem(STORAGE_KEY)
      set({ token: null, role: null, userId: null })
    }
  }
})

export type { Role }
