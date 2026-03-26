import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { api } from '../lib/api'

interface User {
  id: string
  email: string
  full_name: string
  is_ca: boolean
  firm_name?: string
  is_active: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: any) => Promise<void>
  logout: () => void
  updateUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email: string, password: string) => {
        const response = await api.post('/auth/login', {
          username: email,
          password,
        })
        
        const { access_token, user } = response.data
        
        set({
          token: access_token,
          user,
          isAuthenticated: true,
        })
        
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      },

      register: async (data: any) => {
        await api.post('/auth/register', data)
        await get().login(data.email, data.password)
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
        delete api.defaults.headers.common['Authorization']
      },

      updateUser: (userData: Partial<User>) => {
        const currentUser = get().user
        if (currentUser) {
          set({ user: { ...currentUser, ...userData } })
        }
      },
    }),
    {
      name: 'taxmind-auth',
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
)
