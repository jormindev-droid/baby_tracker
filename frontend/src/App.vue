<template>
  <div id="app">
    <header v-if="showHeader" class="app-header">
      <div class="container">
        <div class="header-content">
          <h1>宝宝成长记录</h1>
          <nav v-if="isAuthenticated" class="nav-menu">
            <router-link to="/">首页</router-link>
            <router-link to="/children">我的宝宝</router-link>
            <button @click="logout" class="logout-btn">退出登录</button>
          </nav>
        </div>
      </div>
    </header>
    
    <main class="app-main">
      <router-view />
    </main>
    
    <footer class="app-footer">
      <div class="container">
        <p>&copy; 2024 宝宝成长记录 - 记录宝宝的每一个成长瞬间</p>
      </div>
    </footer>
  </div>
</template>

<script>
import { mapState, mapActions } from 'pinia'
import { useAuthStore } from './stores/auth'

export default {
  name: 'App',
  computed: {
    ...mapState(useAuthStore, ['isAuthenticated']),
    showHeader() {
      return this.$route.meta.requiresAuth || this.$route.meta.guestOnly
    }
  },
  methods: {
    ...mapActions(useAuthStore, ['logout'])
  }
}
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: #fff;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
}

.header-content h1 {
  margin: 0;
  color: #333;
  font-size: 1.5rem;
}

.nav-menu {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.nav-menu a {
  text-decoration: none;
  color: #666;
  font-weight: 500;
  transition: color 0.3s ease;
}

.nav-menu a:hover,
.nav-menu a.router-link-active {
  color: #4CAF50;
}

.logout-btn {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-weight: 500;
  transition: color 0.3s ease;
}

.logout-btn:hover {
  color: #4CAF50;
}

.app-main {
  flex: 1;
  padding: 2rem 0;
}

.app-footer {
  background: #f8f8f8;
  border-top: 1px solid #e0e0e0;
  padding: 1rem 0;
  margin-top: auto;
}

.app-footer p {
  margin: 0;
  text-align: center;
  color: #666;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav-menu {
    gap: 1rem;
  }
}
</style>