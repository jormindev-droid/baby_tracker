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
        console.log('开始获取宝宝列表...')
        const response = await axios.get('/api/children')
        console.log('获取宝宝列表成功:', response.data)
        this.children = response.data
        console.log('store中的children已更新:', this.children)
      } catch (error) {
        console.error('获取宝宝列表失败:', error)
      }
    },
    
    async addChild(childData) {
      try {
        console.log('开始添加宝宝:', childData)
        const response = await axios.post('/api/children', childData)
        console.log('添加宝宝成功:', response.data)
        await this.fetchChildren()
        return { success: true, message: response.data.message }
      } catch (error) {
        console.error('添加宝宝失败:', error)
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