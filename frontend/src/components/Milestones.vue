<template>
  <div class="milestones">
    <div class="container">
      <div class="milestones-header">
        <h2>成长里程碑</h2>
        <div class="header-actions">
          <button @click="showAddModal = true" class="btn btn-primary">
            添加里程碑
          </button>
        </div>
      </div>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="milestones.length === 0" class="empty-state">
        <div class="empty-icon">🎉</div>
        <h3>还没有成长里程碑</h3>
        <p>点击上方按钮记录宝宝的重要时刻</p>
      </div>
      
      <div v-else class="milestones-content">
        <div class="timeline">
          <div 
            v-for="milestone in milestones" 
            :key="milestone.id" 
            class="timeline-item"
          >
            <div class="timeline-marker">
              <div class="marker-icon">🎉</div>
            </div>
            <div class="timeline-content">
              <div class="milestone-card">
                <div class="milestone-header">
                  <h3>{{ milestone.title }}</h3>
                  <div class="milestone-date">
                    {{ formatDate(milestone.date_achieved) }}
                  </div>
                </div>
                <div v-if="milestone.description" class="milestone-description">
                  {{ milestone.description }}
                </div>
                <div class="milestone-actions">
                  <button @click="editMilestone(milestone)" class="btn btn-outline btn-sm">编辑</button>
                  <button @click="deleteMilestone(milestone.id)" class="btn btn-danger btn-sm">删除</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加/编辑里程碑模态框 -->
    <div v-if="showAddModal || editingMilestone" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingMilestone ? '编辑里程碑' : '添加里程碑' }}</h3>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        <form @submit.prevent="handleSaveMilestone" class="modal-form">
          <div class="form-group">
            <label>里程碑标题</label>
            <input 
              v-model="formData.title" 
              type="text" 
              required 
              placeholder="例如: 第一次翻身"
            />
          </div>
          <div class="form-group">
            <label>达成日期</label>
            <input 
              v-model="formData.date_achieved" 
              type="date" 
              required 
            />
          </div>
          <div class="form-group">
            <label>详细描述 <span class="optional">(可选)</span></label>
            <textarea 
              v-model="formData.description"
              placeholder="描述这个里程碑的详细情况..."
              rows="4"
            ></textarea>
          </div>
          <div v-if="formError" class="error-message">{{ formError }}</div>
          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

export default {
  name: 'Milestones',
  props: {
    child: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const route = useRoute()
    const loading = ref(false)
    const milestones = ref([])
    const showAddModal = ref(false)
    const editingMilestone = ref(null)
    const saving = ref(false)
    const formError = ref('')
    
    const formData = ref({
      title: '',
      date_achieved: '',
      description: ''
    })

    const fetchMilestones = async () => {
      loading.value = true
      try {
        const response = await axios.get(`/api/children/${props.child.id}/milestones`)
        milestones.value = response.data.sort((a, b) => new Date(b.date_achieved) - new Date(a.date_achieved))
      } catch (error) {
        console.error('获取里程碑失败:', error)
      } finally {
        loading.value = false
      }
    }

    const addMilestone = async () => {
      try {
        await axios.post(`/api/children/${props.child.id}/milestones`, formData.value)
        await fetchMilestones()
        showAddModal.value = false
        resetForm()
      } catch (error) {
        formError.value = '添加里程碑失败'
      }
    }

    const updateMilestone = async () => {
      try {
        await axios.put(`/api/children/${props.child.id}/milestones/${editingMilestone.value.id}`, formData.value)
        await fetchMilestones()
        editingMilestone.value = null
        showAddModal.value = false
        resetForm()
      } catch (error) {
        formError.value = '更新里程碑失败'
      }
    }

    const deleteMilestone = async (milestoneId) => {
      if (!confirm('确定要删除这个里程碑吗？')) return
      
      try {
        await axios.delete(`/api/children/${props.child.id}/milestones/${milestoneId}`)
        await fetchMilestones()
      } catch (error) {
        console.error('删除里程碑失败:', error)
      }
    }

    const editMilestone = (milestone) => {
      editingMilestone.value = milestone
      formData.value = {
        title: milestone.title,
        date_achieved: milestone.date_achieved,
        description: milestone.description || ''
      }
      showAddModal.value = true
    }

    const handleSaveMilestone = async () => {
      formError.value = ''
      
      if (!formData.value.title || !formData.value.date_achieved) {
        formError.value = '请填写必填字段'
        return
      }

      saving.value = true
      
      try {
        if (editingMilestone.value) {
          await updateMilestone()
        } else {
          await addMilestone()
        }
      } finally {
        saving.value = false
      }
    }

    const closeModal = () => {
      showAddModal.value = false
      editingMilestone.value = null
      resetForm()
    }

    const resetForm = () => {
      formData.value = {
        title: '',
        date_achieved: '',
        description: ''
      }
      formError.value = ''
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
    }

    onMounted(() => {
      fetchMilestones()
    })

    watch(() => props.child.id, () => {
      fetchMilestones()
    })

    return {
      loading,
      milestones,
      showAddModal,
      editingMilestone,
      saving,
      formError,
      formData,
      formatDate,
      handleSaveMilestone,
      editMilestone,
      deleteMilestone,
      closeModal
    }
  }
}
</script>

<style scoped>
.milestones {
  padding: 2rem 0;
}

.milestones-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3rem;
}

.milestones-header h2 {
  margin: 0;
  color: #333;
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

.timeline {
  position: relative;
  padding-left: 3rem;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 20px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #eee;
}

.timeline-item {
  position: relative;
  margin-bottom: 3rem;
}

.timeline-marker {
  position: absolute;
  left: -2.5rem;
  top: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #4CAF50;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.marker-icon {
  font-size: 1.5rem;
}

.timeline-content {
  margin-left: 2rem;
}

.milestone-card {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  border-left: 4px solid #4CAF50;
}

.milestone-card:hover {
  transform: translateX(5px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.15);
}

.milestone-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.milestone-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.25rem;
}

.milestone-date {
  background: #f8f9fa;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  color: #666;
  border: 1px solid #e9ecef;
}

.milestone-description {
  color: #666;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.milestone-actions {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-sm {
  padding: 0.25rem 0.75rem;
  font-size: 0.8rem;
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

.btn-danger {
  background: #d32f2f;
  color: white;
}

.btn-danger:hover {
  background: #c62828;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  max-width: 600px;
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

.optional {
  color: #888;
  font-weight: normal;
}

.form-group input,
.form-group textarea {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 120px;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.error-message {
  color: #d32f2f;
  background: #ffebee;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #ffcdd2;
}

@media (max-width: 768px) {
  .milestones-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .timeline {
    padding-left: 0;
  }
  
  .timeline::before {
    left: 20px;
  }
  
  .timeline-marker {
    left: -20px;
  }
  
  .timeline-content {
    margin-left: 0;
    margin-top: 2rem;
  }
  
  .milestone-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .modal {
    margin: 1rem;
    max-width: none;
  }
}
</style>