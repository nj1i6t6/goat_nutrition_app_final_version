<!-- START OF FILE frontend/src/views/ChatView.vue -->
<template>
  <div>
    <h2>AI 問答助理</h2>
    <Card>
      <div class="chat-controls">
        <label for="selectChatContextEarNum">針對羊隻 (選填):</label>
        <select id="selectChatContextEarNum" v-model="selectedEarNum">
            <option value="">一般問答</option>
            <option v-for="sheep in flockStore.sheepCache" :key="sheep.id" :value="sheep.EarNum">
                {{ sheep.EarNum }}
            </option>
        </select>
        <input type="text" v-model="manualEarNumInput" @keydown.enter="findEarNum" class="manual-earnum-input" placeholder="或手動輸入耳號查詢">
        <button @click="findEarNum" class="action-button small">查詢</button>
        <button @click="clearChat" class="action-button secondary-button">清空對話</button>
      </div>

      <div class="chat-container" ref="chatContainer">
        <div v-for="(msg, index) in chatHistory" :key="index" class="chat-message" :class="msg.role">
            <div v-if="msg.role === 'model'" v-html="msg.content"></div>
            <p v-else>{{ msg.content }}</p>
        </div>
        <div v-if="isLoading" class="chat-message model typing-indicator">
            <span></span><span></span><span></span>
        </div>
      </div>
      
      <div class="chat-input-area">
        <textarea v-model="userMessage" @keydown.enter.prevent.exact="sendMessage" placeholder="輸入您的問題..." rows="2"></textarea>
        <!-- 【重要修正】:disabled 條件直接讀取 authStore.apiKey -->
        <button @click="sendMessage" :disabled="isLoading || !authStore.apiKey">發送</button>
      </div>
      <p v-if="!authStore.apiKey" class="form-note-error">請先在「系統設定」頁面設定有效的 API 金鑰。</p>
      <div v-if="error" class="status-tag error" style="margin-top: 15px;">{{ error }}</div>
    </Card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useFlockStore } from '@/stores/flock'
import * as api from '@/services/api'
import Card from '@/components/Card.vue'

const authStore = useAuthStore()
const flockStore = useFlockStore()

const sessionId = ref('session_' + Date.now())
const chatHistory = reactive([{ role: 'model', content: '<p>您好，我是領頭羊博士，請問有什麼可以為您服務的嗎？</p>' }])
const userMessage = ref('')
const selectedEarNum = ref('')
const manualEarNumInput = ref('')
const isLoading = ref(false)
const error = ref('')
const chatContainer = ref(null)

function findEarNum() {
    const earNumToFind = manualEarNumInput.value.trim();
    if (!earNumToFind) return;
    const exists = flockStore.sheepCache.some(sheep => sheep.EarNum === earNumToFind);
    if (exists) {
        selectedEarNum.value = earNumToFind;
        manualEarNumInput.value = '';
        alert(`已成功定位到羊隻 ${earNumToFind}。`);
    } else {
        alert(`錯誤：在您的羊群中找不到耳號為 ${earNumToFind} 的羊隻。`);
    }
}

async function sendMessage() {
    const message = userMessage.value.trim();
    if (!message || isLoading.value || !authStore.apiKey) return;

    chatHistory.push({ role: 'user', content: message });
    userMessage.value = '';
    isLoading.value = true;
    error.value = '';
    scrollToBottom();

    try {
        const result = await api.chatWithAgent(authStore.apiKey, message, sessionId.value, selectedEarNum.value);
        chatHistory.push({ role: 'model', content: result.reply_html });
    } catch (e) {
        error.value = `回覆錯誤: ${e.message}`;
        chatHistory.push({ role: 'model', content: `<p style="color:red;">抱歉，我遇到一個問題，暫時無法回覆。</p>` });
    } finally {
        isLoading.value = false;
        scrollToBottom();
    }
}

function clearChat() {
    sessionId.value = 'session_' + Date.now();
    chatHistory.length = 0;
    chatHistory.push({ role: 'model', content: '<p>您好，我是領頭羊博士，請問有什麼可以為您服務的嗎？</p>' });
    error.value = '';
    alert("對話歷史已清除。");
}

async function scrollToBottom() {
    await nextTick();
    if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
}

onMounted(() => {
    if (flockStore.sheepCache.length === 0) {
        flockStore.fetchSheep();
    }
});
</script>

<style scoped>
h2 { font-size: 1.8em; color: #1e3a8a; margin-top: 0; margin-bottom: 25px; padding-bottom: 12px; border-bottom: 2px solid #d1d5db; }
.chat-controls { display:flex; flex-wrap: wrap; gap:10px; align-items:center; margin-bottom: 15px; }
.chat-controls label { margin-bottom:0; white-space:nowrap; font-weight: 500; }
.chat-controls select { flex-grow:1; min-width:150px; max-width: 250px; padding: 8px 10px; border-radius: 6px; border: 1px solid #d1d5db; }
.manual-earnum-input { padding: 8px 10px; border-radius: 6px; border: 1px solid #d1d5db; width: 180px; }
.chat-container { height: 50vh; min-height: 300px; overflow-y: auto; border: 1px solid #e5e7eb; padding: 20px; border-radius: 8px; margin-bottom: 20px; background-color: #ffffff; display: flex; flex-direction: column; }
.chat-message { margin-bottom: 15px; padding: 12px 18px; border-radius: 12px; max-width: 80%; word-wrap: break-word; line-height: 1.5; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.chat-message.user { background-color: #3b82f6; color: white; align-self: flex-end; border-bottom-right-radius: 3px; }
.chat-message.model { background-color: #e5e7eb; color: #374151; align-self: flex-start; border-bottom-left-radius: 3px; }
.chat-input-area { display: flex; gap: 12px; align-items: flex-end; }
.chat-input-area textarea { flex-grow: 1; resize: none; padding:12px 15px; border-radius: 6px; border: 1px solid #d1d5db; }
.action-button { background-color: #3b82f6; color: white; padding: 10px 18px; border: none; border-radius: 6px; cursor: pointer; font-size: 1em; font-weight: 500; }
.action-button.small { padding: 8px 12px; font-size: 0.9em; }
.action-button.secondary-button { background-color: #6b7280; margin-left:auto; }
.chat-input-area button { height: auto; padding: 12px 22px; white-space:nowrap; border-radius: 6px; border: none; background-color: #3b82f6; color: white; cursor: pointer; }
.chat-input-area button:disabled { background-color: #93c5fd; cursor: not-allowed; }
.form-note-error { color: #b91c1c; font-size: 0.9em; margin-top: 10px; }
.status-tag.error { background-color: #fee2e2; color: #991b1b; padding: 10px; border-radius: 6px; }
.typing-indicator span { height: 8px; width: 8px; background-color: #9ca3af; border-radius: 50%; display: inline-block; animation: wave 1.4s infinite ease-in-out both; }
.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
@keyframes wave { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1.0); } }
</style>
<!-- END OF FILE frontend/src/views/ChatView.vue -->