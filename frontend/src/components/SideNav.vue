<!-- START OF FILE frontend/src/components/SideNav.vue -->
<template>
  <ul class="main-nav" :class="{ open: isOpen }">
    <li><RouterLink to="/" class="nav-link" @click="closeNav">代理人儀表板</RouterLink></li>
    <li><RouterLink to="/consultation" class="nav-link" @click="closeNav">飼養建議諮詢</RouterLink></li>
    <li><RouterLink to="/chat" class="nav-link" @click="closeNav">AI 問答助理</RouterLink></li>
    <li><RouterLink to="/flock" class="nav-link" @click="closeNav">羊群總覽</RouterLink></li>
    <li><RouterLink to="/data-management" class="nav-link" @click="closeNav">數據管理</RouterLink></li>
    <li><RouterLink to="/settings" class="nav-link" @click="closeNav">系統設定</RouterLink></li>
  </ul>
</template>

<script setup>
import { RouterLink } from 'vue-router'

// 定義此元件可以接收的屬性 (props) 和可以發出的事件 (emits)
defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['close'])

function closeNav() {
  emit('close')
}
</script>

<style scoped>
/* 樣式與舊專案的 main-nav 保持一致，但更適合 Vue 的響應式設計 */
.main-nav {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  gap: 10px;
}

.main-nav li a {
  display: block;
  padding: 10px 15px;
  color: #e2e8f0;
  text-decoration: none;
  transition: background-color 0.2s, color 0.2s;
  font-size: 0.95em;
  border-radius: 6px;
  font-weight: 500;
}

.main-nav li a:hover {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

/* .router-link-exact-active 是 Vue Router 自動為當前活動連結添加的 class */
.main-nav li a.router-link-exact-active {
  background-color: #2563eb;
  color: white;
}

/* 手機版樣式 */
@media (max-width: 992px) {
  .main-nav {
    display: none; /* 預設隱藏 */
    position: fixed;
    top: 60px; /* 頂部導航列的高度 */
    right: -260px; /* 初始位置在畫面外 */
    width: 260px;
    height: calc(100% - 60px);
    background-color: #2d3748;
    box-shadow: -2px 0 5px rgba(0, 0, 0, 0.2);
    transition: right 0.3s ease-in-out;
    z-index: 999;
    flex-direction: column; /* 改為垂直排列 */
    gap: 0;
    overflow-y: auto;
  }

  .main-nav.open {
    display: flex;
    right: 0; /* 滑入畫面 */
  }

  .main-nav li a {
    padding: 15px 20px;
    border-bottom: 1px solid #4a5568;
    border-radius: 0;
  }
}
</style>
<!-- END OF FILE frontend/src/components/SideNav.vue -->