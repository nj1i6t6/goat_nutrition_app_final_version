// --- START OF FILE frontend/src/stores/flock.js ---

import { reactive, computed, toRefs } from 'vue'
import { defineStore } from 'pinia'
import * as api from '@/services/api'

export const useFlockStore = defineStore('flock', () => {
  const getInitialState = () => ({
    sheepCache: [],
    isLoading: true,
    error: null,
    filters: { farmNum: '', breed: '', sex: '', breedCategory: '', status: '', startDate: '', endDate: '' },
    sort: { key: 'EarNum', direction: 'asc' }
  });

  const state = reactive(getInitialState());

  const filteredAndSortedSheep = computed(() => {
    let result = [...state.sheepCache];
    result = result.filter(sheep => {
        if (state.filters.farmNum && sheep.FarmNum !== state.filters.farmNum) return false;
        if (state.filters.breed && sheep.Breed !== state.filters.breed) return false;
        if (state.filters.sex && sheep.Sex !== state.filters.sex) return false;
        if (state.filters.breedCategory && sheep.breed_category !== state.filters.breedCategory) return false;
        if (state.filters.status && sheep.status !== state.filters.status) return false;
        if (sheep.BirthDate) {
            try {
                const birthDate = new Date(sheep.BirthDate.replace(/-/g, '/'));
                if (state.filters.startDate && birthDate < new Date(state.filters.startDate)) return false;
                if (state.filters.endDate && birthDate > new Date(state.filters.endDate)) return false;
            } catch(e) {}
        } else if (state.filters.startDate || state.filters.endDate) { return false; }
        return true;
    });
    result.sort((a, b) => {
        let valA = a[state.sort.key] || ''; let valB = b[state.sort.key] || '';
        if (state.sort.key === 'BirthDate') { valA = valA ? new Date(valA.replace(/-/g, '/')).getTime() : 0; valB = valB ? new Date(valB.replace(/-/g, '/')).getTime() : 0; }
        if (valA < valB) { return state.sort.direction === 'asc' ? -1 : 1; }
        if (valA > valB) { return state.sort.direction === 'asc' ? 1 : -1; }
        return 0;
    });
    return result;
  });

  const filterOptions = computed(() => {
    const farmNums = [...new Set(state.sheepCache.map(s => s.FarmNum).filter(Boolean))].sort();
    const breeds = [...new Set(state.sheepCache.map(s => s.Breed).filter(Boolean))].sort();
    return { farmNums, breeds };
  });

  // 【新增 Getter】根據耳號查找羊隻
  const getSheepByEarNum = computed(() => {
    return (earNum) => state.sheepCache.find(s => s.EarNum === earNum);
  });

  async function fetchSheep() {
    state.isLoading = true;
    state.error = null;
    try {
      state.sheepCache = await api.getAllSheep();
    } catch (e) {
      state.error = `載入羊隻列表失敗: ${e.message}`;
    } finally {
      state.isLoading = false;
    }
  }

  function setSort(key) {
    if (state.sort.key === key) {
      state.sort.direction = state.sort.direction === 'asc' ? 'desc' : 'asc';
    } else {
      state.sort.key = key;
      state.sort.direction = 'asc';
    }
  }

  function resetFilters() {
    Object.assign(state.filters, getInitialState().filters);
  }
  
  function $reset() {
    Object.assign(state, getInitialState());
  }

  return {
    ...toRefs(state),
    filteredAndSortedSheep,
    filterOptions,
    getSheepByEarNum, // 【新增】導出 getter
    fetchSheep,
    setSort,
    resetFilters,
    $reset
  }
})
// --- END OF FILE frontend/src/stores/flock.js ---