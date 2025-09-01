import axios, { AxiosError, AxiosRequestConfig } from 'axios'
import { useAuthStore } from '../stores/auth'

// Create a singleton axios instance with baseURL proxied to /api
export const http = axios.create({ baseURL: '/api', timeout: 15000 })

http.interceptors.request.use((config: AxiosRequestConfig) => {
  const token = useAuthStore.getState().token
  if (token) config.headers = { ...config.headers, Authorization: `Bearer ${token}` }
  return config
})

http.interceptors.response.use(undefined, (error: AxiosError) => {
  // Optional: global error handling
  return Promise.reject(error)
})
