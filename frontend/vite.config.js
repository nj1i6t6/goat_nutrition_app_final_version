// --- START OF FILE frontend/vite.config.js ---

import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  // 【修正】使用單一、清晰的代理規則
  server: {
    proxy: {
      // 所有以 /api 開頭的請求，都轉發給後端
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      }
    }
  }
})

// --- END OF FILE frontend/vite.config.js ---