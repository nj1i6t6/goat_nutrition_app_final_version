// --- START OF FILE frontend/src/stores/dashboard.js ---

import { reactive, toRefs } from 'vue'
import { defineStore } from 'pinia'
import * as api from '@/services/api'
import { useAuthStore } from './auth'

export const useDashboardStore = defineStore('dashboard', () => {
  const getInitialState = () => ({
    hasLoadedOnce: false,
    isLoading: false,
    error: null,
    hasSheep: false,
    dashboardData: {},
    isTipLoading: false,
    agentTipHtml: '',
    tipError: '',
  });

  const state = reactive(getInitialState());

  async function fetchDashboardDataIfNeeded() {
    if (state.hasLoadedOnce) return;

    state.isLoading = true;
    state.error = null;
    try {
      const [sheepList, data] = await Promise.all([
        api.getAllSheep(),
        api.getDashboardData()
      ]);
      state.hasSheep = sheepList.length > 0;
      if (state.hasSheep) {
        state.dashboardData = data;
      }
      state.hasLoadedOnce = true;
    } catch (e) {
      state.error = `加載儀表板數據失敗: ${e.message}`;
      state.hasSheep = false;
    } finally {
      state.isLoading = false;
    }
  }

  async function fetchAgentTipIfNeeded() {
    if (state.agentTipHtml || state.tipError) return;

    // 【重要修正】在函數執行時，才去獲取 authStore 的實例和 apiKey
    const authStore = useAuthStore();
    const currentApiKey = authStore.apiKey;

    if (!currentApiKey) {
      state.tipError = "請先在「系統設定」中設定有效的API金鑰以獲取提示。";
      state.isTipLoading = false; // 確保停止加載動畫
      return;
    }
    
    state.isTipLoading = true;
    state.tipError = '';
    try {
      const result = await api.getAgentTip(currentApiKey); // 使用即時獲取的金鑰
      state.agentTipHtml = result.tip_html;
    } catch (e) {
      state.tipError = `無法獲取提示: ${e.message}`;
    } finally {
      state.isTipLoading = false;
    }
  }

  function $reset() {
    Object.assign(state, getInitialState());
  }

  return {
    ...toRefs(state),
    fetchDashboardDataIfNeeded,
    fetchAgentTipIfNeeded,
    $reset
  }
})

// --- END OF FILE frontend/src/stores/dashboard.js ---