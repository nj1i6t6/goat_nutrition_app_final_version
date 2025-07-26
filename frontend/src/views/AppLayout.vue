<!-- START OF FILE frontend/src/views/AppLayout.vue -->
<template>
  <div class="app-shell">
    <nav class="top-nav">
      <RouterLink to="/" class="logo">
        <img src="/goat-logo.svg" alt="領頭羊博士 Logo" />
        <span>領頭羊博士</span>
      </RouterLink>
      
      <div class="desktop-nav-container">
        <SideNav :is-open="true" @close="closeNav" />
      </div>

      <div class="user-info">
        <span id="usernameDisplay">{{ authStore.username }}</span>
        <a href="#" @click.prevent="authStore.logout()" class="action-button small">登出</a>
        
        <div class="hamburger-menu">
          <button @click="toggleNav" :aria-expanded="isNavOpen.toString()" aria-label="開啟選單">
            ☰
          </button>
        </div>
      </div>
    </nav>

    <!-- 手機版側滑導航 -->
    <div class="mobile-nav-container">
        <SideNav :is-open="isNavOpen" @close="closeNav" />
    </div>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import SideNav from '@/components/SideNav.vue'

const authStore = useAuthStore()
const isNavOpen = ref(false)

function toggleNav() {
  isNavOpen.value = !isNavOpen.value
}

function closeNav() {
  isNavOpen.value = false
}
</script>

<style scoped>
.app-shell { display: flex; flex-direction: column; min-height: 100vh; background-color: #eef1f5; }
.top-nav { background-color: #3b82f6; color: white; padding: 0 20px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); height: 60px; position: sticky; top: 0; z-index: 1000; }
.logo { font-size: 1.6em; font-weight: bold; display: flex; align-items: center; text-decoration: none; color: white; }
.logo img { height: 32px; margin-right: 10px; }
.user-info { display: flex; align-items: center; gap: 15px; margin-left: auto; }
#usernameDisplay { font-weight: 500; }
.action-button.small { font-size: 0.85em; padding: 7px 12px; margin: 0; background-color: #2563eb; text-decoration: none; white-space: nowrap; }
.main-content { flex-grow: 1; padding: 25px; max-width: 1300px; margin: 0 auto; width: 100%; box-sizing: border-box; }
.desktop-nav-container { margin-left: 20px; }
.hamburger-menu { display: none; }
.hamburger-menu button { background: none; border: none; color: white; font-size: 2em; cursor: pointer; padding: 0 10px; }

@media (max-width: 992px) {
  .desktop-nav-container { display: none; }
  .hamburger-menu { display: block; }
  .user-info { margin-left: 0; }
}
</style>
<!-- END OF FILE frontend/src/views/AppLayout.vue -->