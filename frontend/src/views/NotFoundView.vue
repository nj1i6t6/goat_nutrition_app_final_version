<!-- START OF FILE frontend/src/views/NotFoundView.vue -->
<template>
  <div class="not-found-container">
    <h1>404 - 頁面不存在</h1>
    <p>抱歉，您要找的頁面不存在。</p>
    <RouterLink to="/" class="action-button">返回首頁</RouterLink>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router';
</script>

<style scoped>
.not-found-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60vh;
  text-align: center;
}
h1 {
  color: #1e3a8a;
}
.action-button {
    background-color: #3b82f6; color: white; padding: 11px 22px;
    border: none; border-radius: 6px; cursor: pointer;
    font-size: 1em; font-weight: 500;
    text-decoration: none;
    margin-top: 20px;
}
</style>
<!-- END OF FILE frontend/src/views/NotFoundView.vue -->