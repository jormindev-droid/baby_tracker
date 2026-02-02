import { defineStore } from 'pinia'
import axios from 'axios'

export const useChildrenStore = defineStore('children', {
  state: () => ({
    children: [],
    currentChild: null
  }),
  
  actions: {
    async fetchChildren() {
      try {
        const response = await axios.get('/api/children')
        this.children = response.data
      } catch (error) {
        console.error('获取宝宝列表失败:', error)
      }
    },
    
    async addChild(childData) {
      try {
        const response = await axios.post('/api/children', childData)
        await this.fetchChildren()
        return { success: true, message: response.data.message }
      } catch (error) {
        return { success: false, message: error.response?.data?.message || '添加宝宝失败' }
      }
    },
    
    async updateCurrentChild(childId) {
      this.currentChild = this.children.find(child => child.id === childId)
    },
    
    clearCurrentChild() {
      this.currentChild = null
    }
  }
})