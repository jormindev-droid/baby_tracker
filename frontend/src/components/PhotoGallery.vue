<template>
  <div class="photo-gallery">
    <div class="container">
      <div class="gallery-header">
        <h2>照片管理</h2>
        <div class="header-actions">
          <label class="btn btn-primary file-upload-label">
            上传照片
            <input 
              type="file" 
              ref="fileInput"
              @change="handleFileSelect"
              accept="image/*"
              class="file-input"
            />
          </label>
        </div>
      </div>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="photos.length === 0" class="empty-state">
        <div class="empty-icon">📸</div>
        <h3>还没有照片</h3>
        <p>点击上方按钮上传宝宝的第一张照片</p>
      </div>
      
      <div v-else class="gallery-content">
        <div class="upload-progress" v-if="uploading">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
          </div>
          <p>上传中... {{ uploadProgress }}%</p>
        </div>
        
        <div class="photo-grid">
          <div 
            v-for="photo in photos" 
            :key="photo.id" 
            class="photo-card"
            @click="openLightbox(photo)"
          >
            <img :src="getPhotoUrl(photo.filename)" :alt="photo.description || '宝宝照片'" />
            <div class="photo-overlay">
              <div class="photo-info">
                <h4>{{ formatDate(photo.date_taken) }}</h4>
                <p v-if="photo.description">{{ photo.description }}</p>
              </div>
              <div class="photo-actions">
                <button @click.stop="deletePhoto(photo.id)" class="btn btn-danger btn-sm">删除</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 照片预览模态框 -->
    <div v-if="lightboxPhoto" class="lightbox-overlay" @click="closeLightbox">
      <div class="lightbox-content" @click.stop>
        <button class="lightbox-close" @click="closeLightbox">×</button>
        <img :src="getPhotoUrl(lightboxPhoto.filename)" :alt="lightboxPhoto.description || '宝宝照片'" />
        <div class="lightbox-info">
          <h3>{{ formatDate(lightboxPhoto.date_taken) }}</h3>
          <p v-if="lightboxPhoto.description">{{ lightboxPhoto.description }}</p>
        </div>
      </div>
    </div>
    
    <!-- 添加照片描述模态框 -->
    <div v-if="showDescriptionModal" class="modal-overlay" @click="showDescriptionModal = false">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>添加照片描述</h3>
          <button @click="showDescriptionModal = false" class="close-btn">×</button>
        </div>
        <form @submit.prevent="handleUploadPhoto" class="modal-form">
          <div class="form-group">
            <label>照片描述</label>
            <textarea 
              v-model="photoDescription"
              placeholder="描述这张照片，比如宝宝在做什么..."
              rows="4"
            ></textarea>
          </div>
          <div v-if="uploadError" class="error-message">{{ uploadError }}</div>
          <div class="modal-actions">
            <button type="button" @click="showDescriptionModal = false" class="btn btn-secondary">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="uploading">
              {{ uploading ? '上传中...' : '上传' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

export default {
  name: 'PhotoGallery',
  props: {
    child: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const route = useRoute()
    const loading = ref(false)
    const photos = ref([])
    const uploading = ref(false)
    const uploadProgress = ref(0)
    const uploadError = ref('')
    const lightboxPhoto = ref(null)
    const showDescriptionModal = ref(false)
    const photoDescription = ref('')
    const selectedFile = ref(null)
    const fileInput = ref(null)

    const fetchPhotos = async () => {
      loading.value = true
      try {
        const response = await axios.get(`/api/children/${props.child.id}/photos`)
        photos.value = response.data.sort((a, b) => new Date(b.date_taken) - new Date(a.date_taken))
      } catch (error) {
        console.error('获取照片失败:', error)
      } finally {
        loading.value = false
      }
    }

    const getPhotoUrl = (filename) => {
      return `/uploads/${filename}`
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
    }

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        if (!file.type.startsWith('image/')) {
          alert('请选择图片文件')
          return
        }
        
        selectedFile.value = file
        photoDescription.value = ''
        showDescriptionModal.value = true
      }
    }

    const handleUploadPhoto = async () => {
      if (!selectedFile.value) return
      
      uploadError.value = ''
      uploading.value = true
      uploadProgress.value = 0
      
      const formData = new FormData()
      formData.append('photo', selectedFile.value)
      formData.append('description', photoDescription.value)
      
      try {
        const response = await axios.post(`/api/children/${props.child.id}/photos`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          }
        })
        
        await fetchPhotos()
        showDescriptionModal.value = false
        selectedFile.value = null
        photoDescription.value = ''
        fileInput.value.value = ''
      } catch (error) {
        uploadError.value = '上传失败，请检查文件大小和格式'
        console.error('上传照片失败:', error)
      } finally {
        uploading.value = false
        uploadProgress.value = 0
      }
    }

    const deletePhoto = async (photoId) => {
      if (!confirm('确定要删除这张照片吗？')) return
      
      try {
        await axios.delete(`/api/children/${props.child.id}/photos/${photoId}`)
        await fetchPhotos()
      } catch (error) {
        console.error('删除照片失败:', error)
      }
    }

    const openLightbox = (photo) => {
      lightboxPhoto.value = photo
    }

    const closeLightbox = () => {
      lightboxPhoto.value = null
    }

    onMounted(() => {
      fetchPhotos()
    })

    watch(() => props.child.id, () => {
      fetchPhotos()
    })

    return {
      loading,
      photos,
      uploading,
      uploadProgress,
      uploadError,
      lightboxPhoto,
      showDescriptionModal,
      photoDescription,
      fileInput,
      getPhotoUrl,
      formatDate,
      handleFileSelect,
      handleUploadPhoto,
      deletePhoto,
      openLightbox,
      closeLightbox
    }
  }
}
</script>

<style scoped>
.photo-gallery {
  padding: 2rem 0;
}

.gallery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3rem;
}

.gallery-header h2 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.file-upload-label {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  margin: 0;
}

.file-input {
  display: none;
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

.upload-progress {
  background: white;
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #eee;
  border-radius: 4px;
  margin-bottom: 0.5rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #4CAF50;
  transition: width 0.3s ease;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 2rem;
}

.photo-card {
  position: relative;
  border-radius: 15px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
  cursor: pointer;
  height: 200px;
}

.photo-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 15px rgba(0,0,0,0.2);
}

.photo-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.photo-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  padding: 1.5rem;
  color: white;
  transform: translateY(100%);
  transition: transform 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.photo-card:hover .photo-overlay {
  transform: translateY(0);
}

.photo-info h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}

.photo-info p {
  margin: 0;
  font-size: 0.875rem;
  opacity: 0.9;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.photo-actions {
  display: flex;
  gap: 0.5rem;
}

.lightbox-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.lightbox-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.lightbox-content img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  display: block;
  border-radius: 8px;
}

.lightbox-close {
  position: absolute;
  top: -40px;
  right: 0;
  background: none;
  border: none;
  color: white;
  font-size: 2rem;
  cursor: pointer;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.3s ease;
}

.lightbox-close:hover {
  background: rgba(255,255,255,0.1);
}

.lightbox-info {
  position: absolute;
  bottom: -60px;
  left: 0;
  right: 0;
  color: white;
  text-align: center;
}

.lightbox-info h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.25rem;
}

.lightbox-info p {
  margin: 0;
  font-size: 1rem;
  opacity: 0.9;
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

.form-group textarea {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  resize: vertical;
  min-height: 120px;
  transition: border-color 0.3s ease;
}

.form-group textarea:focus {
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

.error-message {
  color: #d32f2f;
  background: #ffebee;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #ffcdd2;
}

@media (max-width: 768px) {
  .gallery-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .photo-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1rem;
  }
  
  .photo-card {
    height: 150px;
  }
  
  .lightbox-content {
    max-width: 100vw;
    max-height: 100vh;
  }
  
  .lightbox-close {
    top: -50px;
  }
  
  .modal {
    margin: 1rem;
    max-width: none;
  }
}
</style>