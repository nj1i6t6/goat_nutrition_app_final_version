<!-- START OF FILE frontend/src/App.vue -->
<template>
  <div v-if="authStore.isLoading" class="full-page-loader">
    <div class="loader"></div>
    <p>正在驗證身份...</p>
  </div>
  <RouterView v-else />
</template>

<script setup>
import { RouterView } from 'vue-router'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()
// 在 App 首次掛載時，觸發一次身份驗證檢查
authStore.verifyAuth()
</script>

<style>
/* 全域樣式，不使用 scoped */
#app {
  font-family: 'Noto Sans TC', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

body {
  margin: 0;
  font-family: 'Noto Sans TC', 'Roboto', sans-serif;
  color: #334155;
  line-height: 1.65;
  font-size: 15px;
}

.full-page-loader {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.full-page-loader p {
  margin-top: 20px;
  font-size: 1.2em;
  color: #6b7280;
}

.loader {
  border: 5px solid #f3f4f6;
  border-top: 5px solid #3b82f6;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

</style>
<!-- END OF FILE frontend/src/App.vue -->