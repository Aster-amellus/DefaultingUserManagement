import { create } from 'zustand'

type Role = 'Admin' | 'Reviewer' | 'Operator'

interface AuthState {
  token: string | null
  role: Role | null
  setAuth: (token: string, role: Role) => void
  clear: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  role: null,
  setAuth: (token, role) => set({ token, role }),
  clear: () => set({ token: null, role: null })
}))
