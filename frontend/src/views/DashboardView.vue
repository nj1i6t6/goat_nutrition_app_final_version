<!-- START OF FILE frontend/src/views/DashboardView.vue -->
<template>
  <div>
    <div v-if="dashboardStore.isLoading" class="loader-container">
        <div class="loader"></div><p>正在加載儀表板...</p>
    </div>
    <div v-else-if="!dashboardStore.hasSheep" class="card">
        <h3>讓我們開始建立您的羊群檔案吧！</h3>
        <div class="welcome-box">
            <h4>第一步：下載標準範本</h4>
            <p>請先下載系統提供的標準 Excel 範本...</p>
            <a href="/download_template" class="action-button" download>下載標準範本.xlsx</a>
            <hr>
            <h4>第二步：前往數據管理中心</h4>
            <p>將您的資料填入範本後，點擊下方按鈕前往導入。</p>
            <RouterLink to="/data-management" class="action-button consult">🚀 前往數據管理中心</RouterLink>
        </div>
    </div>
    <div v-else>
        <h2>代理人儀表板</h2>
        <div class="card">
            <h3 class="card-title">領頭羊博士的問候！</h3>
            <div v-if="dashboardStore.isTipLoading" class="loader small-loader"></div>
            <div v-else-if="dashboardStore.tipError" class="tip-error">{{ dashboardStore.tipError }}</div>
            <div v-else v-html="dashboardStore.agentTipHtml" class="tip-content"></div>
        </div>
        <div class="grid-layout">
            <div class="card">
                <h3 class="card-title"><span class="emoji-icon">⚠️</span> 待辦提醒</h3>
                <div v-if="dashboardStore.isLoading" class="loader small-loader"></div>
                <ul v-else-if="dashboardStore.dashboardData.reminders?.length > 0">
                    <li v-for="r in dashboardStore.dashboardData.reminders" :key="r.ear_num + r.type">
                        <a href="#">{{ r.ear_num }}</a>: {{ r.type }} ({{ r.due_date }}) - 
                        <span class="status-tag" :class="r.status === '已過期' ? 'error' : 'warning'">{{ r.status }}</span>
                    </li>
                </ul>
                <p v-else class="status-tag neutral">暫無待辦提醒。</p>
            </div>
            <div class="card">
                <h3 class="card-title"><span class="emoji-icon">❗️</span> 健康警示</h3>
                <div v-if="dashboardStore.isLoading" class="loader small-loader"></div>
                <ul v-else-if="dashboardStore.dashboardData.health_alerts?.length > 0">
                     <li v-for="(alert, index) in dashboardStore.dashboardData.health_alerts" :key="index" class="alert-item">
                        <a href="#" class="alert-earnum">{{ alert.ear_num }}</a> - 
                        <span class="status-tag error">{{ alert.type }}</span>
                        <p class="alert-message">{{ alert.message }}</p>
                    </li>
                </ul>
                <p v-else class="status-tag neutral">暫無偵測到健康警示。</p>
            </div>
            <div class="card">
                <h3 class="card-title"><span class="emoji-icon">🐑</span> 羊群狀態速覽</h3>
                <div v-if="dashboardStore.isLoading" class="loader small-loader"></div>
                <div v-else-if="dashboardStore.dashboardData.flock_status_summary?.length > 0">
                    <p v-for="s in dashboardStore.dashboardData.flock_status_summary" :key="s.status">
                        <strong>{{ getStatusText(s.status) }}:</strong> {{ s.count }} 隻
                    </p>
                </div>
                <p v-else class="status-tag neutral">暫無羊群狀態數據。</p>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { RouterLink } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'

const dashboardStore = useDashboardStore()

// 【修正】元件掛載時，呼叫新的 "IfNeeded" 方法
onMounted(() => {
    dashboardStore.fetchDashboardDataIfNeeded();
    dashboardStore.fetchAgentTipIfNeeded();
});

const statusOptions = [
    {value:"maintenance",text:"維持期"}, {value:"growing_young",text:"生長前期"}, {value:"growing_finishing",text:"生長育肥期"},
    {value:"gestating_early",text:"懷孕早期"}, {value:"gestating_late",text:"懷孕晚期"}, {value:"lactating_early",text:"泌乳早期"},
    {value:"lactating_peak",text:"泌乳高峰期"}, {value:"lactating_mid",text:"泌乳中期"}, {value:"lactating_late",text:"泌乳晚期"},
    {value:"dry_period",text:"乾乳期"}
];
const getStatusText = (value) => statusOptions.find(o => o.value === value)?.text || value || '未分類';

function openModal(earNum, tab) {
  alert(`功能開發中：打開羊隻 ${earNum} 的彈窗，並顯示 ${tab} 頁籤。`);
}
</script>

<style scoped>
.loader-container { text-align: center; padding: 60px 0; }
.grid-layout { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 25px; }
.card { background-color: #ffffff; border-radius: 8px; padding: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 25px; }
h2 { font-size: 1.8em; color: #1e3a8a; margin-top: 0; margin-bottom: 25px; padding-bottom: 12px; border-bottom: 2px solid #d1d5db; }
h3 { font-size: 1.4em; color: #1e40af; margin-top: 0; margin-bottom: 18px; }
.card-title { font-size: 1.2em; color: #1e40af; }
.welcome-box { margin-top: 25px; padding: 20px; border: 1px solid #d1d5db; border-radius: 8px; background-color: #f9fafb; }
.welcome-box h4 { margin-top: 0; }
.welcome-box hr { margin: 20px 0; border: 0; border-top: 1px solid #d1d5db; }
ul { list-style: none; padding: 0; }
li { padding: 8px 0; border-bottom: 1px solid #f3f4f6; }
li:last-child { border-bottom: none; }
.alert-item { margin-bottom: 12px; }
.alert-earnum { font-weight: bold; }
.alert-message { margin: 5px 0 0 0; font-size: 0.9em; color: #555; }
.emoji-icon { font-size:1.2em; margin-right:5px; }
.status-tag { padding: 4px 10px; border-radius: 14px; font-size: 0.8em; font-weight: 500; display: inline-block; line-height: 1.2; }
.status-tag.error   { background-color: #fee2e2; color: #991b1b; }
.status-tag.warning { background-color: #fef9c3; color: #854d0e; }
.status-tag.neutral { background-color: #e5e7eb; color: #4b5563; }
.action-button { background-color: #3b82f6; color: white; padding: 11px 22px; border: none; border-radius: 6px; cursor: pointer; font-size: 1em; font-weight: 500; text-decoration: none; display: inline-block; }
.action-button.consult { background-color: #22c55e; font-size: 1.1em; padding: 12px 25px; }
.tip-content { font-size: 1em; color: #4b5563; font-style: italic; }
.tip-error { color: orange; }
.small-loader { width: 20px; height: 20px; margin: 5px 0; border-width: 3px; }
</style>
<!-- END OF FILE frontend/src/views/DashboardView.vue --->