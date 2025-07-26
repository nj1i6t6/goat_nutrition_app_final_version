<!-- START OF FILE frontend/src/views/LoginView.vue -->
<template>
  <div class="login-page-body">
    <div class="login-container">
      <div class="login-logo">
        <img src="/goat-logo.svg" alt="領頭羊博士 Logo" />
        <h1>領頭羊博士</h1>
        <p>您的智能飼養顧問</p>
      </div>

      <div class="form-toggle-buttons">
        <button
          id="showLoginBtn"
          class="toggle-btn"
          :class="{ active: currentForm === 'login' }"
          @click="switchForm('login')"
        >
          登入
        </button>
        <button
          id="showRegisterBtn"
          class="toggle-btn"
          :class="{ active: currentForm === 'register' }"
          @click="switchForm('register')"
        >
          註冊
        </button>
      </div>

      <!-- 登入表單 -->
      <form v-if="currentForm === 'login'" @submit.prevent="handleLogin" class="auth-form active">
        <div class="form-group">
          <label for="login_username">使用者名稱</label>
          <input type="text" id="login_username" v-model="loginData.username" required autocomplete="username" />
        </div>
        <div class="form-group">
          <label for="login_password">密碼</label>
          <input type="password" id="login_password" v-model="loginData.password" required autocomplete="current-password" />
        </div>
        <button type="submit" class="action-button full-width" :disabled="authStore.isLoading">
          {{ authStore.isLoading ? '處理中...' : '登入' }}
        </button>
      </form>

      <!-- 註冊表單 -->
      <form v-if="currentForm === 'register'" @submit.prevent="handleRegister" class="auth-form active">
        <div class="form-group">
          <label for="register_username">使用者名稱</label>
          <input type="text" id="register_username" v-model="registerData.username" required autocomplete="username" />
        </div>
        <div class="form-group">
          <label for="register_password">密碼</label>
          <input type="password" id="register_password" v-model="registerData.password" required autocomplete="new-password" />
        </div>
        <p class="form-note">請設定至少6位數的密碼。</p>
        <button type="submit" class="action-button full-width" :disabled="authStore.isLoading">
          {{ authStore.isLoading ? '處理中...' : '註冊並登入' }}
        </button>
      </form>

      <div v-if="authStore.authError" class="status-message error">
        {{ authStore.authError }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const currentForm = ref('login')

const loginData = reactive({
  username: '',
  password: ''
})

const registerData = reactive({
  username: '',
  password: ''
})

function switchForm(formName) {
  currentForm.value = formName
  authStore.authError = null
}

async function handleLogin() {
  // 現在只調用 store 的方法，不關心跳轉邏輯
  await authStore.login(loginData.username, loginData.password)
}

async function handleRegister() {
  if (registerData.password.length < 6) {
    authStore.authError = '錯誤: 密碼長度至少需要6位'
    return
  }
  // 只調用 store 的方法，不關心跳轉邏輯
  await authStore.register(registerData.username, registerData.password)
}
</script>

<style scoped>
/* 樣式保持不變 */
.login-page-body { display: flex; justify-content: center; align-items: center; min-height: 100vh; background-color: #f0f4f8; font-family: 'Noto Sans TC', sans-serif; }
.login-container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); width: 100%; max-width: 400px; text-align: center; }
.login-logo { margin-bottom: 25px; }
.login-logo img { height: 50px; margin-bottom: 10px; }
.login-logo h1 { margin: 0; font-size: 2em; color: #1e3a8a; }
.login-logo p { margin-top: 5px; color: #64748b; }
.form-toggle-buttons { display: flex; margin-bottom: 25px; background-color: #eef1f5; border-radius: 8px; padding: 5px; }
.toggle-btn { flex: 1; padding: 10px; border: none; background: transparent; cursor: pointer; font-size: 1em; font-weight: 500; color: #64748b; border-radius: 6px; transition: all 0.3s ease; }
.toggle-btn.active { background-color: white; color: #3b82f6; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08); }
.auth-form { display: block; }
.form-group { text-align: left; margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 500; color: #4b5563; }
input[type='text'], input[type='password'] { width: 100%; padding: 12px 15px; border: 1px solid #d1d5db; border-radius: 6px; box-sizing: border-box; font-size: 0.95em; background-color: #f9fafb; }
.action-button.full-width { width: 100%; padding: 14px; font-size: 1.1em; margin-top: 10px; background-color: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500; transition: background-color 0.2s ease; }
.action-button:disabled { background-color: #93c5fd; cursor: not-allowed; }
.form-note { font-size: 0.85em; color: #94a3b8; margin-top: -10px; margin-bottom: 20px; text-align: left; }
.status-message { margin-top: 20px; padding: 12px; border-radius: 6px; font-weight: 500; }
.status-message.error { background-color: #fee2e2; color: #991b1b; }
</style>
<!-- END OF FILE frontend/src/views/LoginView.vue -->