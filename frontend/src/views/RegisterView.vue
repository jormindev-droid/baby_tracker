<template>
  <div class="register">
    <div class="container">
      <div class="register-card">
        <h2>注册账号</h2>
        <form @submit.prevent="handleRegister">
          <div class="form-group">
            <label for="username">用户名</label>
            <input
              type="text"
              id="username"
              v-model="username"
              required
              placeholder="请输入用户名"
            />
          </div>
          <div class="form-group">
            <label for="password">密码</label>
            <input
              type="password"
              id="password"
              v-model="password"
              required
              placeholder="请输入密码"
            />
          </div>
          <div class="form-group">
            <label for="confirmPassword">确认密码</label>
            <input
              type="password"
              id="confirmPassword"
              v-model="confirmPassword"
              required
              placeholder="请确认密码"
            />
          </div>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div v-if="success" class="success-message">{{ success }}</div>
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? '注册中...' : '注册' }}
          </button>
        </form>
        <div class="register-footer">
          <p>已有账号？<router-link to="/login">立即登录</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'RegisterView',
  setup() {
    const username = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const error = ref('')
    const success = ref('')
    const loading = ref(false)
    const router = useRouter()
    const authStore = useAuthStore()

    const handleRegister = async () => {
      error.value = ''
      success.value = ''

      if (!username.value || !password.value || !confirmPassword.value) {
        error.value = '请填写所有必填字段'
        return
      }

      if (password.value !== confirmPassword.value) {
        error.value = '两次输入的密码不一致'
        return
      }

      if (password.value.length < 6) {
        error.value = '密码长度至少6位'
        return
      }

      loading.value = true

      try {
        const result = await authStore.register(username.value, password.value)
        
        if (result.success) {
          success.value = result.message
          setTimeout(() => {
            router.push('/login')
          }, 1500)
        } else {
          error.value = result.message
        }
      } catch (err) {
        error.value = '注册失败，请检查网络连接'
      } finally {
        loading.value = false
      }
    }

    return {
      username,
      password,
      confirmPassword,
      error,
      success,
      loading,
      handleRegister
    }
  }
}
</script>

<style scoped>
.register {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}

.register-card {
  background: white;
  padding: 3rem;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}

.register-card h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #666;
}

.form-group input {
  width: 100%;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.error-message {
  color: #d32f2f;
  background: #ffebee;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  border: 1px solid #ffcdd2;
}

.success-message {
  color: #2e7d32;
  background: #e8f5e9;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  border: 1px solid #c8e6c9;
}

.btn {
  width: 100%;
  padding: 1rem;
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
  transform: translateY(-1px);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.register-footer {
  text-align: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #eee;
}

.register-footer p {
  color: #666;
  margin: 0;
}

.register-footer a {
  color: #4CAF50;
  text-decoration: none;
  font-weight: 600;
}

.register-footer a:hover {
  text-decoration: underline;
}
</style>