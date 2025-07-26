<!-- START OF FILE frontend/src/components/Card.vue -->
<template>
  <div class="card">
    <slot></slot>
  </div>
</template>

<script setup>
// 這是一個純展示性的元件，不需要腳本邏輯
</script>

<style scoped>
.card {
  background-color: #ffffff;
  border-radius: 8px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.06);
  margin-bottom: 25px;
}
</style>
<!-- END OF FILE frontend/src/components/Card.vue -->