<template>
  <div class="children">
    <div class="container">
      <div class="page-header">
        <h1>我的宝宝</h1>
        <button @click="showAddModal = true" class="btn btn-primary">
          添加宝宝
        </button>
      </div>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="children.length === 0" class="empty-state">
        <div class="empty-icon">👶</div>
        <h3>还没有宝宝信息</h3>
        <p>点击上方按钮添加您的第一个宝宝</p>
      </div>
      
      <div v-else class="children-grid">
        <div 
          v-for="child in children" 
          :key="child.id" 
          class="child-card"
          @click="$router.push(`/child/${child.id}/growth`)"
        >
          <div class="child-avatar">
            {{ getAvatarText(child.name) }}
          </div>
          <div class="child-info">
            <h3>{{ child.name }}</h3>
            <p class="child-details">
              {{ getAgeText(child.birth_date) }} • {{ child.gender === 'male' ? '男' : '女' }}
            </p>
            <div class="child-stats">
              <span v-if="child.latestGrowth">
                身高 {{ child.latestGrowth.height }}cm
              </span>
              <span v-if="child.latestGrowth">
                体重 {{ child.latestGrowth.weight }}kg
              </span>
              <span>{{ child.photos_count || 0 }} 张照片</span>
              <span>{{ child.milestones_count || 0 }} 个里程碑</span>
            </div>
          </div>
          <div class="child-actions">
            <button 
              @click.stop="$router.push(`/child/${child.id}/growth`)" 
              class="btn btn-outline"
            >
              查看详情
            </button>
          </div>
        </div>
      </div>
      
      <!-- 调试信息 -->
      <div class="debug-info" v-if="children.length > 0">
        <p>宝宝数量: {{ children.length }}</p>
        <button @click="debugStore" class="btn btn-small">调试Store</button>
      </div>
    </div>
    
    <!-- 添加宝宝模态框 -->
    <div v-if="showAddModal" class="modal-overlay" @click="showAddModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>添加宝宝</h3>
          <button @click="showAddModal = false" class="close-btn">×</button>
        </div>
        <form @submit.prevent="handleAddChild" class="modal-form">
          <div class="form-group">
            <label>宝宝姓名</label>
            <input v-model="newChild.name" type="text" placeholder="请输入宝宝姓名" required />
          </div>
          <div class="form-group">
            <label>出生日期</label>
            <input v-model="newChild.birth_date" type="date" required />
          </div>
          <div class="form-group">
            <label>性别</label>
            <select v-model="newChild.gender" required>
              <option value="male">男</option>
              <option value="female">女</option>
            </select>
          </div>
          <div v-if="addError" class="error-message">{{ addError }}</div>
          <div class="modal-actions">
            <button type="button" @click="showAddModal = false" class="btn btn-secondary">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="addLoading">
              {{ addLoading ? '添加中...' : '添加' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useChildrenStore } from '../stores/children'

export default {
  name: 'ChildrenView',
  setup() {
    const router = useRouter()
    const childrenStore = useChildrenStore()
    
    const loading = ref(false)
    const showAddModal = ref(false)
    const addLoading = ref(false)
    const addError = ref('')
    
    const newChild = ref({
      name: '',
      birth_date: '',
      gender: 'male'
    })

    const fetchChildren = async () => {
      loading.value = true
      try {
        await childrenStore.fetchChildren()
      } catch (error) {
        console.error('获取宝宝列表失败:', error)
      } finally {
        loading.value = false
      }
    }

    const handleAddChild = async () => {
      addError.value = ''
      addLoading.value = true
      
      try {
        const result = await childrenStore.addChild(newChild.value)
        
        if (result.success) {
          showAddModal.value = false
          newChild.value = { name: '', birth_date: '', gender: 'male' }
          await fetchChildren()
        } else {
          addError.value = result.message
        }
      } catch (error) {
        addError.value = '添加失败，请检查网络连接'
      } finally {
        addLoading.value = false
      }
    }

    const getAvatarText = (name) => {
      return name ? name.charAt(0).toUpperCase() : '?'
    }

    const getAgeText = (birthDate) => {
      const birth = new Date(birthDate)
      const today = new Date()
      const diffMs = today - birth
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
      
      if (diffDays < 30) {
        return `${diffDays}天`
      } else if (diffDays < 365) {
        const months = Math.floor(diffDays / 30)
        return `${months}个月`
      } else {
        const years = Math.floor(diffDays / 365)
        const months = Math.floor((diffDays % 365) / 30)
        return `${years}岁${months}个月`
      }
    }

    const debugStore = () => {
      console.log('=== ChildrenView Debug ===')
      console.log('children from store:', childrenStore.children)
      console.log('children length:', childrenStore.children.length)
      console.log('children computed:', childrenStore.children)
      childrenStore.debugState()
    }

    onMounted(() => {
      fetchChildren()
    })

    return {
      children: childrenStore.children,
      loading,
      showAddModal,
      addLoading,
      addError,
      newChild,
      handleAddChild,
      getAvatarText,
      getAgeText,
      debugStore
    }
  }
}
</script>

<style scoped>
.children {
  padding: 2rem 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3rem;
}

.page-header h1 {
  margin: 0;
  color: #333;
}

.children-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
}

.child-card {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.child-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.15);
}

.child-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
  font-weight: bold;
  flex-shrink: 0;
}

.child-info {
  flex: 1;
}

.child-info h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.5rem;
}

.child-details {
  margin: 0 0 1rem 0;
  color: #666;
  font-size: 1rem;
}

.child-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.9rem;
  color: #888;
}

.child-stats span {
  background: #f8f9fa;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  border: 1px solid #e9ecef;
}

.child-actions {
  flex-shrink: 0;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 4rem;
  color: #666;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  color: #333;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.3s ease;
}

.close-btn:hover {
  background: #f8f9fa;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #333;
}

.form-group input,
.form-group select {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #45a049;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-outline {
  background: transparent;
  border: 1px solid #4CAF50;
  color: #4CAF50;
}

.btn-outline:hover {
  background: #4CAF50;
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: #d32f2f;
  background: #ffebee;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #ffcdd2;
}

@media (max-width: 768px) {
  .child-card {
    flex-direction: column;
    align-items: flex-start;
    text-align: center;
  }
  
  .child-actions {
    align-self: center;
  }
  
  .modal {
    margin: 1rem;
    max-width: none;
  }
}
</style>