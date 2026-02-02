<template>
  <div class="child-detail">
    <div class="container">
      <div class="child-header">
        <div class="child-info">
          <div class="avatar">{{ getAvatarText(child?.name) }}</div>
          <div>
            <h1>{{ child?.name }}</h1>
            <p class="child-meta">
              {{ getAgeText(child?.birth_date) }} • {{ child?.gender === 'male' ? '男' : '女' }}
            </p>
          </div>
        </div>
        <div class="header-actions">
          <button @click="$router.push('/children')" class="btn btn-secondary">返回列表</button>
        </div>
      </div>
      
      <div v-if="!child" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else class="content">
        <nav class="nav-tabs">
          <router-link 
            :to="`/child/${child.id}/growth`" 
            class="tab-item"
            active-class="active"
          >
            成长记录
          </router-link>
          <router-link 
            :to="`/child/${child.id}/photos`" 
            class="tab-item"
            active-class="active"
          >
            照片管理
          </router-link>
          <router-link 
            :to="`/child/${child.id}/milestones`" 
            class="tab-item"
            active-class="active"
          >
            成长里程碑
          </router-link>
        </nav>
        
        <div class="tab-content">
          <router-view :child="child" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useChildrenStore } from '../stores/children'

export default {
  name: 'ChildDetailView',
  setup() {
    const route = useRoute()
    const childrenStore = useChildrenStore()
    
    const child = ref(null)
    const loading = ref(false)

    const fetchChild = async () => {
      loading.value = true
      try {
        await childrenStore.fetchChildren()
        const childId = parseInt(route.params.id)
        child.value = childrenStore.children.find(c => c.id === childId)
        
        if (!child.value) {
          // 如果找不到宝宝，可能需要从服务器获取
          console.error('未找到宝宝信息')
        }
      } catch (error) {
        console.error('获取宝宝信息失败:', error)
      } finally {
        loading.value = false
      }
    }

    const getAvatarText = (name) => {
      return name ? name.charAt(0).toUpperCase() : '?'
    }

    const getAgeText = (birthDate) => {
      if (!birthDate) return ''
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

    onMounted(() => {
      fetchChild()
    })

    watch(() => route.params.id, () => {
      fetchChild()
    })

    return {
      child,
      loading,
      getAvatarText,
      getAgeText
    }
  }
}
</script>

<style scoped>
.child-detail {
  padding: 2rem 0;
}

.child-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #eee;
}

.child-info {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 3rem;
  font-weight: bold;
}

.child-info h1 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 2.5rem;
}

.child-meta {
  margin: 0;
  color: #666;
  font-size: 1.1rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
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

.nav-tabs {
  display: flex;
  border-bottom: 1px solid #eee;
  margin-bottom: 2rem;
}

.tab-item {
  padding: 1rem 2rem;
  text-decoration: none;
  color: #666;
  font-weight: 600;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
  position: relative;
}

.tab-item:hover {
  color: #4CAF50;
  background: #f8f9fa;
}

.tab-item.active {
  color: #4CAF50;
  border-bottom-color: #4CAF50;
  background: #f8f9fa;
}

.tab-content {
  min-height: 400px;
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

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

@media (max-width: 768px) {
  .child-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .child-info {
    gap: 1rem;
  }
  
  .avatar {
    width: 80px;
    height: 80px;
    font-size: 2.5rem;
  }
  
  .child-info h1 {
    font-size: 2rem;
  }
  
  .nav-tabs {
    flex-direction: column;
  }
  
  .tab-item {
    border-bottom: none;
    border-right: 3px solid transparent;
    text-align: left;
  }
  
  .tab-item.active {
    border-right-color: #4CAF50;
    border-bottom: none;
  }
}
</style>