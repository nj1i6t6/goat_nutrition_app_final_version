// --- START OF FILE frontend/src/stores/auth.js ---

import { ref, computed, watch } from 'vue' // 【修正】導入 watch
import { defineStore } from 'pinia'
import { useRouter } from 'vue-router'
import { checkAuthStatus, login as apiLogin, register as apiRegister, logout as apiLogout, getAgentTip } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)
  const authError = ref(null)
  const isLoading = ref(true)
  
  // 1. 從 localStorage 初始化 apiKey
  const apiKey = ref(localStorage.getItem('geminiApiKey') || '')
  
  const apiKeyStatus = ref({ valid: false, message: '' })

  const username = computed(() => (user.value ? user.value.username : ''))
  const router = useRouter()

  // 2. 【核心修正】使用 watch 建立 apiKey 和 localStorage 之間的雙向同步
  watch(apiKey, (newKey) => {
    if (newKey) {
      // 當 apiKey 有值時，寫入 localStorage
      localStorage.setItem('geminiApiKey', newKey);
    } else {
      // 當 apiKey 變為空時，從 localStorage 移除
      localStorage.removeItem('geminiApiKey');
    }
  });

  async function verifyAuth() {
    isLoading.value = true;
    try {
      const data = await checkAuthStatus()
      if (data.logged_in) {
        user.value = { username: data.username }
        isAuthenticated.value = true
        // 【新增】驗證登入後，重新從快取讀取一次 key，確保同步
        apiKey.value = localStorage.getItem('geminiApiKey') || '';
      } else {
        user.value = null
        isAuthenticated.value = false
      }
    } catch (error) {
      console.error('驗證身份失敗:', error)
      user.value = null
      isAuthenticated.value = false
    } finally {
      isLoading.value = false
    }
  }

  async function loginAndSetup(apiFunc, username, password) {
    isLoading.value = true
    authError.value = null
    try {
      await apiFunc(username, password)
      await verifyAuth() // verifyAuth 內部會處理好 apiKey 的重新讀取
      router.push('/')
      return true
    } catch (error) {
      authError.value = error.message
      return false
    } finally {
      isLoading.value = false
    }
  }
  const login = (username, password) => loginAndSetup(apiLogin, username, password);
  const register = (username, password) => loginAndSetup(apiRegister, username, password);
  
  async function logout() {
    const { useFlockStore } = await import('./flock');
    const { useDashboardStore } = await import('./dashboard');
    useDashboardStore().$reset();
    useFlockStore().$reset();

    try { await apiLogout(); } 
    catch (error) { console.error('請求後端登出時發生錯誤:', error); } 
    finally {
      user.value = null;
      isAuthenticated.value = false;
      apiKey.value = ''; // 這裡會觸發 watch，自動從 localStorage 移除
      router.push('/login');
    }
  }
  
  async function testAndSaveApiKey(keyToTest) {
    if (!keyToTest) {
      apiKeyStatus.value = { valid: false, message: '請輸入 API 金鑰。' };
      return;
    }
    apiKeyStatus.value = { valid: false, message: '正在測試金鑰...' };
    try {
      await getAgentTip(keyToTest);
      apiKey.value = keyToTest; // 這裡會觸發 watch，自動寫入 localStorage
      apiKeyStatus.value = { valid: true, message: 'API 金鑰驗證成功！已儲存。' };
    } catch (error) {
      apiKeyStatus.value = { valid: false, message: `金鑰驗證失敗: ${error.message}` };
      apiKey.value = ''; // 觸發 watch 移除錯誤的金鑰
    }
  }
  
  return {
    user, isAuthenticated, authError, isLoading, username,
    apiKey, apiKeyStatus, verifyAuth, login, register, logout, testAndSaveApiKey
  }
})
// --- END OF FILE frontend/src/stores/auth.js ---