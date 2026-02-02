import { defineStore } from 'pinia'
import axios from 'axios'

export const useChildrenStore = defineStore('children', {
  state: () => ({
    children: [],
    currentChild: null
  }),
  
  getters: {
    childrenCount: (state) => state.children.length,
    childrenNames: (state) => state.children.map(child => child.name)
  },
  
  actions: {
    async fetchChildren() {
      try {
        console.log('开始获取宝宝列表...')
        const response = await axios.get('/api/children')
        console.log('获取宝宝列表成功:', response.data)
        // 确保使用响应式赋值
        this.children = response.data
        console.log('store中的children已更新:', this.children)
        console.log('children数组长度:', this.children.length)
      } catch (error) {
        console.error('获取宝宝列表失败:', error)
      }
    },
    
    async addChild(childData) {
      try {
        console.log('开始添加宝宝:', childData)
        const response = await axios.post('/api/children', childData)
        console.log('添加宝宝成功:', response.data)
        // 立即将新宝宝添加到本地数组
        if (response.data.child) {
          this.children.push(response.data.child)
          console.log('已添加到本地数组:', this.children)
        }
        // 然后重新获取完整列表
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
    },
    
    // 调试方法
    debugState() {
      console.log('=== Children Store Debug ===')
      console.log('children数组:', this.children)
      console.log('children长度:', this.children.length)
      console.log('children内容:', JSON.stringify(this.children))
      console.log('currentChild:', this.currentChild)
      console.log('=== End Debug ===')
    }
  }
})
