<template>
  <div class="growth-chart">
    <div class="container">
      <div class="chart-header">
        <h2>成长记录</h2>
        <div class="header-actions">
          <button @click="showAddModal = true" class="btn btn-primary">
            添加记录
          </button>
        </div>
      </div>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="records.length === 0" class="empty-state">
        <div class="empty-icon">📈</div>
        <h3>还没有成长记录</h3>
        <p>点击上方按钮添加第一条成长记录</p>
      </div>
      
      <div v-else class="chart-content">
        <div class="charts-grid">
          <div class="chart-card">
            <h3>身高变化</h3>
            <div class="chart-container">
              <LineChart :data="heightChartData" />
            </div>
          </div>
          <div class="chart-card">
            <h3>体重变化</h3>
            <div class="chart-container">
              <LineChart :data="weightChartData" />
            </div>
          </div>
          <div class="chart-card" v-if="hasHeadCircumference">
            <h3>头围变化</h3>
            <div class="chart-container">
              <LineChart :data="headCircumferenceChartData" />
            </div>
          </div>
        </div>
        
        <div class="records-list">
          <h3>详细记录</h3>
          <div class="record-items">
            <div 
              v-for="record in records" 
              :key="record.id" 
              class="record-item"
            >
              <div class="record-date">
                {{ formatDate(record.date_recorded) }}
              </div>
              <div class="record-data">
                <span class="data-item">
                  <strong>身高:</strong> {{ record.height }} cm
                </span>
                <span class="data-item">
                  <strong>体重:</strong> {{ record.weight }} kg
                </span>
                <span v-if="record.head_circumference" class="data-item">
                  <strong>头围:</strong> {{ record.head_circumference }} cm
                </span>
              </div>
              <div class="record-actions">
                <button @click="editRecord(record)" class="btn btn-outline btn-sm">编辑</button>
                <button @click="deleteRecord(record.id)" class="btn btn-danger btn-sm">删除</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加/编辑记录模态框 -->
    <div v-if="showAddModal || editingRecord" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingRecord ? '编辑记录' : '添加记录' }}</h3>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        <form @submit.prevent="handleSaveRecord" class="modal-form">
          <div class="form-group">
            <label>记录日期</label>
            <input 
              v-model="formData.date_recorded" 
              type="date" 
              required 
            />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>身高 (cm)</label>
              <input 
                v-model.number="formData.height" 
                type="number" 
                step="0.1" 
                min="0"
                required 
                placeholder="例如: 75.5"
              />
            </div>
            <div class="form-group">
              <label>体重 (kg)</label>
              <input 
                v-model.number="formData.weight" 
                type="number" 
                step="0.1" 
                min="0"
                required 
                placeholder="例如: 9.2"
              />
            </div>
          </div>
          <div class="form-group">
            <label>头围 (cm) <span class="optional">(可选)</span></label>
            <input 
              v-model.number="formData.head_circumference" 
              type="number" 
              step="0.1" 
              min="0"
              placeholder="例如: 45.0"
            />
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
import { Line as LineChart } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import axios from 'axios'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

export default {
  name: 'GrowthChart',
  components: {
    LineChart
  },
  props: {
    child: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const route = useRoute()
    const loading = ref(false)
    const records = ref([])
    const showAddModal = ref(false)
    const editingRecord = ref(null)
    const saving = ref(false)
    const formError = ref('')
    
    const formData = ref({
      date_recorded: '',
      height: '',
      weight: '',
      head_circumference: ''
    })

    const fetchRecords = async () => {
      loading.value = true
      try {
        const response = await axios.get(`/api/children/${props.child.id}/growth`)
        records.value = response.data.sort((a, b) => new Date(a.date_recorded) - new Date(b.date_recorded))
      } catch (error) {
        console.error('获取成长记录失败:', error)
      } finally {
        loading.value = false
      }
    }

    const heightChartData = computed(() => ({
      labels: records.value.map(r => formatDate(r.date_recorded)),
      datasets: [{
        label: '身高 (cm)',
        data: records.value.map(r => r.height),
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        tension: 0.4,
        fill: true
      }]
    }))

    const weightChartData = computed(() => ({
      labels: records.value.map(r => formatDate(r.date_recorded)),
      datasets: [{
        label: '体重 (kg)',
        data: records.value.map(r => r.weight),
        borderColor: '#2196F3',
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        tension: 0.4,
        fill: true
      }]
    }))

    const headCircumferenceChartData = computed(() => ({
      labels: records.value.filter(r => r.head_circumference).map(r => formatDate(r.date_recorded)),
      datasets: [{
        label: '头围 (cm)',
        data: records.value.filter(r => r.head_circumference).map(r => r.head_circumference),
        borderColor: '#FF9800',
        backgroundColor: 'rgba(255, 152, 0, 0.1)',
        tension: 0.4,
        fill: true
      }]
    }))

    const hasHeadCircumference = computed(() => {
      return records.value.some(r => r.head_circumference)
    })

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
    }

    const addRecord = async () => {
      try {
        await axios.post(`/api/children/${props.child.id}/growth`, formData.value)
        await fetchRecords()
        showAddModal.value = false
        resetForm()
      } catch (error) {
        formError.value = '添加记录失败，请检查数据格式'
      }
    }

    const updateRecord = async () => {
      try {
        await axios.put(`/api/children/${props.child.id}/growth/${editingRecord.value.id}`, formData.value)
        await fetchRecords()
        editingRecord.value = null
        showAddModal.value = false
        resetForm()
      } catch (error) {
        formError.value = '更新记录失败，请检查数据格式'
      }
    }

    const deleteRecord = async (recordId) => {
      if (!confirm('确定要删除这条记录吗？')) return
      
      try {
        await axios.delete(`/api/children/${props.child.id}/growth/${recordId}`)
        await fetchRecords()
      } catch (error) {
        console.error('删除记录失败:', error)
      }
    }

    const editRecord = (record) => {
      editingRecord.value = record
      formData.value = {
        date_recorded: record.date_recorded,
        height: record.height,
        weight: record.weight,
        head_circumference: record.head_circumference || ''
      }
      showAddModal.value = true
    }

    const handleSaveRecord = async () => {
      formError.value = ''
      
      if (!formData.value.date_recorded || !formData.value.height || !formData.value.weight) {
        formError.value = '请填写必填字段'
        return
      }
      
      if (formData.value.height <= 0 || formData.value.weight <= 0) {
        formError.value = '身高和体重必须大于0'
        return
      }

      saving.value = true
      
      try {
        if (editingRecord.value) {
          await updateRecord()
        } else {
          await addRecord()
        }
      } finally {
        saving.value = false
      }
    }

    const closeModal = () => {
      showAddModal.value = false
      editingRecord.value = null
      resetForm()
    }

    const resetForm = () => {
      formData.value = {
        date_recorded: '',
        height: '',
        weight: '',
        head_circumference: ''
      }
      formError.value = ''
    }

    onMounted(() => {
      fetchRecords()
    })

    watch(() => props.child.id, () => {
      fetchRecords()
    })

    return {
      loading,
      records,
      showAddModal,
      editingRecord,
      saving,
      formError,
      formData,
      heightChartData,
      weightChartData,
      headCircumferenceChartData,
      hasHeadCircumference,
      formatDate,
      handleSaveRecord,
      editRecord,
      deleteRecord,
      closeModal
    }
  }
}
</script>

<style scoped>
.growth-chart {
  padding: 2rem 0;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3rem;
}

.chart-header h2 {
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

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
}

.chart-card {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.chart-card h3 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.25rem;
}

.chart-container {
  height: 300px;
  position: relative;
}

.records-list {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.records-list h3 {
  margin: 0 0 2rem 0;
  color: #333;
}

.record-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.record-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border: 1px solid #eee;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.record-item:hover {
  border-color: #4CAF50;
  background: #f8f9fa;
}

.record-date {
  font-weight: 600;
  color: #333;
  min-width: 120px;
}

.record-data {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.data-item {
  color: #666;
  font-size: 0.9rem;
}

.data-item strong {
  color: #333;
  margin-right: 0.5rem;
}

.record-actions {
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group label {
  font-weight: 600;
  color: #333;
}

.optional {
  color: #888;
  font-weight: normal;
}

.form-group input {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
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

.error-message {
  color: #d32f2f;
  background: #ffebee;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #ffcdd2;
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .record-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .record-actions {
    align-self: flex-end;
  }
  
  .modal {
    margin: 1rem;
    max-width: none;
  }
}
</style>