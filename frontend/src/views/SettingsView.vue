<!-- START OF FILE frontend/src/views/SettingsView.vue -->
<template>
  <div>
    <h2>系統設定</h2>

    <!-- API 金鑰設定卡片 -->
    <Card>
      <h3>Gemini API 金鑰設定</h3>
      <p>請在此輸入您的 Google Gemini API 金鑰。此金鑰將被儲存在您的瀏覽器本地，用於與領頭羊博士 AI 進行通訊。</p>
      <div class="form-group">
        <label for="geminiApiKeyInput">API 金鑰:</label>
        <input type="password" id="geminiApiKeyInput" v-model="apiKeyInput" placeholder="在此貼上您的 API 金鑰">
      </div>
      <div v-if="authStore.apiKeyStatus.message" class="api-key-status" :class="{ 'success': authStore.apiKeyStatus.valid, 'error': !authStore.apiKeyStatus.valid && authStore.apiKeyStatus.message !== '正在測試金鑰...' , 'info': authStore.apiKeyStatus.message === '正在測試金鑰...' }">
        {{ authStore.apiKeyStatus.message }}
      </div>
      <button @click="handleTestAndSaveApiKey" class="action-button" :disabled="isTestingApiKey">
        {{ isTestingApiKey ? '測試中...' : '測試並儲存金鑰' }}
      </button>
      <p class="form-note">
        提示：如果您沒有 API 金鑰，請前往 
        <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener noreferrer">Google AI Studio</a> 獲取。
      </p>
    </Card>

    <!-- 事件選項管理卡片 -->
    <Card>
      <h3>事件選項管理</h3>
      <p>您可以在這裡自訂事件記錄時的「事件類型」和對應的「簡要描述」選項。預設選項無法刪除。</p>
      
      <div class="event-type-add-form">
          <input type="text" v-model="newEventType" @keyup.enter="handleAddEventType" placeholder="輸入新的事件類型名稱">
          <button @click="handleAddEventType" class="action-button">新增類型</button>
      </div>

      <div v-if="isLoadingOptions" class="loader"></div>
      <div v-else-if="optionsError" class="status-tag error">{{ optionsError }}</div>
      <div v-else class="event-options-container">
        <div v-for="type in eventOptions" :key="type.id" class="event-type-item">
          <div class="event-type-header">
            <h4>{{ type.name }} <span v-if="type.is_default" class="status-tag neutral small-tag">預設</span></h4>
            <button v-if="!type.is_default" @click="handleDeleteEventType(type.id)" class="delete-btn" title="刪除此類型">×</button>
          </div>
          <ul class="event-description-list">
            <li v-for="desc in type.descriptions" :key="desc.id">
              <span>{{ desc.description }}</span>
              <button v-if="!desc.is_default" @click="handleDeleteEventDescription(desc.id)" class="delete-btn" title="刪除此描述">×</button>
            </li>
            <li v-if="!type.descriptions || type.descriptions.length === 0">
              <span class="no-desc-text">尚無簡要描述</span>
            </li>
          </ul>
          <div class="event-description-add-form">
            <input type="text" v-model="newDescriptions[type.id]" @keyup.enter="handleAddEventDescription(type.id)" placeholder="為此類型新增簡要描述">
            <button @click="handleAddEventDescription(type.id)" class="action-button small">新增</button>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import * as api from '@/services/api'
import Card from '@/components/Card.vue' // 導入我們建立的卡片元件

// --- 狀態管理 ---
const authStore = useAuthStore()

// API Key 相關狀態
const apiKeyInput = ref('')
const isTestingApiKey = ref(false)

// 事件選項相關狀態
const eventOptions = ref([])
const isLoadingOptions = ref(true)
const optionsError = ref('')
const newEventType = ref('')
const newDescriptions = reactive({}) // 使用 reactive 物件來儲存每個類型的輸入值

// --- 方法 ---

// API Key 相關方法
async function handleTestAndSaveApiKey() {
  isTestingApiKey.value = true
  await authStore.testAndSaveApiKey(apiKeyInput.value)
  isTestingApiKey.value = false
}

// 事件選項相關方法
async function fetchEventOptions() {
  isLoadingOptions.value = true
  optionsError.value = ''
  try {
    eventOptions.value = await api.getEventOptions()
  } catch (error) {
    optionsError.value = `載入事件選項失敗: ${error.message}`
  } finally {
    isLoadingOptions.value = false
  }
}

async function handleAddEventType() {
  const name = newEventType.value.trim()
  if (!name) {
    alert('請輸入事件類型名稱。')
    return
  }
  try {
    await api.addEventType(name)
    newEventType.value = ''
    await fetchEventOptions() // 重新載入列表
  } catch (error) {
    alert(`新增失敗: ${error.message}`)
  }
}

async function handleDeleteEventType(typeId) {
  if (confirm('確定要刪除此事件類型嗎？其下所有關聯的簡要描述也將一併被刪除。此操作無法復原。')) {
    try {
      await api.deleteEventType(typeId)
      await fetchEventOptions()
    } catch (error) {
      alert(`刪除失敗: ${error.message}`)
    }
  }
}

async function handleAddEventDescription(typeId) {
  const description = newDescriptions[typeId]?.trim()
  if (!description) {
    alert('請輸入簡要描述內容。')
    return
  }
  try {
    await api.addEventDescription(typeId, description)
    newDescriptions[typeId] = '' // 清空輸入框
    await fetchEventOptions()
  } catch (error) {
    alert(`新增失敗: ${error.message}`)
  }
}

async function handleDeleteEventDescription(descriptionId) {
  if (confirm('確定要刪除此簡要描述嗎？')) {
    try {
      await api.deleteEventDescription(descriptionId)
      await fetchEventOptions()
    } catch (error) {
      alert(`刪除失敗: ${error.message}`)
    }
  }
}

// --- 生命週期鉤子 ---
onMounted(() => {
  // 元件掛載時，從 store 載入已儲存的 key 到輸入框
  apiKeyInput.value = authStore.apiKey
  // 載入事件選項
  fetchEventOptions()
})
</script>

<style scoped>
/* 將舊專案中的相關樣式遷移至此 */
h2 {
    font-size: 1.8em;
    color: #1e3a8a;
    margin-top: 0;
    margin-bottom: 25px;
    padding-bottom: 12px;
    border-bottom: 2px solid #d1d5db;
}

h3 {
    font-size: 1.4em;
    color: #1e40af;
    margin-top: 0;
    margin-bottom: 18px;
}

.form-group {
    margin-bottom: 15px;
}

label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #4b5563;
}

input[type="text"], input[type="password"] {
    width: 100%;
    padding: 12px 15px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    box-sizing: border-box;
    font-size: 0.95em;
    background-color: #f9fafb;
}

.api-key-status {
    margin-top: 10px;
    margin-bottom: 15px;
    padding: 10px;
    border-radius: 6px;
    font-weight: 500;
}
.api-key-status.success { background-color: #dcfce7; color: #166534; }
.api-key-status.error { background-color: #fee2e2; color: #991b1b; }
.api-key-status.info { background-color: #dbeafe; color: #1e40af; }


.action-button {
    background-color: #3b82f6; color: white; padding: 11px 22px;
    border: none; border-radius: 6px; cursor: pointer;
    font-size: 1em; font-weight: 500;
    transition: background-color 0.2s ease;
    text-decoration: none;
    display: inline-block;
}
.action-button:disabled {
    background-color: #93c5fd;
    cursor: not-allowed;
}
.action-button.small {
    font-size: 0.9em;
    padding: 8px 14px;
}


.form-note {
    font-size: 0.9em;
    color: #666;
    margin-top: 15px;
}
.form-note a {
    color: #3b82f6;
    text-decoration: none;
}
.form-note a:hover {
    text-decoration: underline;
}

/* 事件選項管理樣式 */
.event-type-add-form {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}
.event-type-add-form input {
    flex-grow: 1;
}

.event-options-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
}

.event-type-item {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 15px;
}

.event-type-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 10px;
    margin-bottom: 10px;
}

.event-type-header h4 {
    margin: 0;
    font-size: 1.1em;
    color: #1e3a8a;
}

.status-tag {
    padding: 4px 10px; border-radius: 14px; font-size: 0.8em;
    font-weight: 500; display: inline-block; line-height: 1.2;
}
.status-tag.neutral { background-color: #e5e7eb; color: #4b5563; }
.status-tag.error { background-color: #fee2e2; color: #991b1b; }

.status-tag.small-tag {
    padding: 2px 6px;
    font-size: 0.7em;
    margin-left: 8px;
    vertical-align: middle;
}

.delete-btn {
    background: none;
    border: none;
    color: #9ca3af;
    font-size: 1.5em;
    cursor: pointer;
    line-height: 1;
    padding: 0 5px;
    transition: color 0.2s;
}
.delete-btn:hover {
    color: #ef4444;
}

.event-description-list {
    list-style: none;
    padding: 0;
    margin: 0 0 15px 0;
    max-height: 150px;
    overflow-y: auto;
}
.event-description-list li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 5px;
    border-bottom: 1px solid #f3f4f6;
    font-size: 0.95em;
}
.event-description-list li:last-child {
    border-bottom: none;
}
.event-description-list li span {
    color: #4b5563;
    word-break: break-all;
}

.no-desc-text {
  font-style: italic;
  color: #9ca3af;
}

.event-description-add-form {
    display: flex;
    gap: 8px;
    margin-top: 10px;
}
.event-description-add-form input {
    flex-grow: 1;
}

</style>
<!-- END OF FILE frontend/src/views/SettingsView.vue -->