<template>
  <div class="home">
    <div class="hero">
      <div class="container">
        <h1>记录宝宝的每一个成长瞬间</h1>
        <p class="hero-subtitle">专业的宝宝成长记录应用，帮助您记录宝宝的身高、体重、照片和成长里程碑</p>
        <div class="hero-actions">
          <router-link to="/children" class="btn btn-primary">开始记录</router-link>
          <router-link to="/children" class="btn btn-secondary">查看宝宝</router-link>
        </div>
      </div>
    </div>
    
    <div class="features">
      <div class="container">
        <h2>主要功能</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">📏</div>
            <h3>成长记录</h3>
            <p>记录宝宝的身高、体重和头围变化，生成成长曲线图</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📸</div>
            <h3>照片管理</h3>
            <p>上传和管理宝宝的照片，按时间轴展示成长点滴</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🎉</div>
            <h3>成长里程碑</h3>
            <p>记录宝宝的重要时刻，如第一次翻身、第一次走路等</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>数据统计</h3>
            <p>生成详细的成长报告和统计图表</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="stats">
      <div class="container">
        <div class="stats-grid">
          <div class="stat-item">
            <h3>{{ childrenCount }}</h3>
            <p>已记录宝宝</p>
          </div>
          <div class="stat-item">
            <h3>{{ photosCount }}</h3>
            <p>照片数量</p>
          </div>
          <div class="stat-item">
            <h3>{{ milestonesCount }}</h3>
            <p>成长里程碑</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'pinia'
import { useChildrenStore } from '../stores/children'

export default {
  name: 'HomeView',
  computed: {
    ...mapState(useChildrenStore, ['children']),
    childrenCount() {
      return this.children.length
    },
    photosCount() {
      return this.children.reduce((total, child) => total + (child.photos?.length || 0), 0)
    },
    milestonesCount() {
      return this.children.reduce((total, child) => total + (child.milestones?.length || 0), 0)
    }
  },
  async mounted() {
    await this.$store.children.fetchChildren()
  }
}
</script>

<style scoped>
.home {
  padding: 0;
}

.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4rem 0;
  text-align: center;
}

.hero h1 {
  font-size: 3rem;
  margin: 0 0 1rem 0;
  font-weight: 700;
}

.hero-subtitle {
  font-size: 1.2rem;
  margin: 0 0 3rem 0;
  opacity: 0.9;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
}

.btn {
  padding: 1rem 2rem;
  border-radius: 50px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.btn-primary {
  background: white;
  color: #667eea;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}

.btn-secondary {
  background: transparent;
  border-color: white;
  color: white;
}

.btn-secondary:hover {
  background: white;
  color: #667eea;
}

.features {
  padding: 4rem 0;
  background: #f8f9fa;
}

.features h2 {
  text-align: center;
  margin-bottom: 3rem;
  font-size: 2.5rem;
  color: #333;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 15px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  margin: 0 0 1rem 0;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

.stats {
  padding: 4rem 0;
  background: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  text-align: center;
}

.stat-item h3 {
  font-size: 3rem;
  margin: 0 0 0.5rem 0;
  color: #4CAF50;
}

.stat-item p {
  font-size: 1.1rem;
  color: #666;
  margin: 0;
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 2rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .features h2 {
    font-size: 2rem;
  }
  
  .stat-item h3 {
    font-size: 2rem;
  }
}
</style>