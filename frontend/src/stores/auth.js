import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: !!localStorage.getItem('token')
  }),
  
  actions: {
    async login(username, password) {
      try {
        const response = await axios.post('/api/login', {
          username,
          password
        })
        
        this.token = response.data.access_token
        this.user = response.data.user_id
        this.isAuthenticated = true
        
        localStorage.setItem('token', this.token)
        return { success: true }
      } catch (error) {
        return { success: false, message: error.response?.data?.message || '登录失败' }
      }
    },
    
    async register(username, password) {
      try {
        const response = await axios.post('/api/register', {
          username,
          password
        })
        
        return { success: true, message: response.data.message }
      } catch (error) {
        return { success: false, message: error.response?.data?.message || '注册失败' }
      }
    },
    
    logout() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
      localStorage.removeItem('token')
    },
    
    initializeAuth() {
      if (this.token) {
        this.isAuthenticated = true
      }
    }
  }
})