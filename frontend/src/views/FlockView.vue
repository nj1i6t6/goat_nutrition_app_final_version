<!-- START OF FILE frontend/src/views/FlockView.vue -->
<template>
  <div>
    <h2>羊群總覽</h2>
    <Card>
      <h3>篩選羊群</h3>
      <div class="filter-grid">
        <div class="filter-item"><label for="filterFarmNum">牧場編號:</label><select id="filterFarmNum" v-model="flockStore.filters.farmNum"><option value="">所有牧場</option><option v-for="num in flockStore.filterOptions.farmNums" :key="num" :value="num">{{ num }}</option></select></div>
        <div class="filter-item"><label for="filterBreed">品種:</label><select id="filterBreed" v-model="flockStore.filters.breed"><option value="">所有品種</option><option v-for="breed in flockStore.filterOptions.breeds" :key="breed" :value="breed">{{ breed }}</option></select></div>
        <div class="filter-item"><label for="filterSex">性別:</label><select id="filterSex" v-model="flockStore.filters.sex"><option value="">所有性別</option><option value="母">母</option><option value="公">公</option><option value="閹">閹</option></select></div>
        <div class="filter-item date-range"><label>出生日期範圍:</label><div><input type="date" v-model="flockStore.filters.startDate"><span>-</span><input type="date" v-model="flockStore.filters.endDate"></div></div>
      </div>
      <div class="filter-actions"><button @click="flockStore.resetFilters()" class="action-button secondary-button">清除篩選</button></div>
    </Card>
    <Card>
      <div class="table-header">
        <button @click="openModal(null)" class="action-button">新增羊隻資料</button>
        <div class="list-summary">共 {{ flockStore.sheepCache.length }} 隻，顯示 {{ flockStore.filteredAndSortedSheep.length }} 隻</div>
      </div>
      <div v-if="flockStore.isLoading" class="loader-container"><div class="loader"></div><p>載入羊隻列表中...</p></div>
      <div v-else-if="flockStore.error" class="status-tag error">{{ flockStore.error }}</div>
      <div v-else class="table-responsive">
        <table id="mainSheepTable">
          <thead><tr>
              <th class="sortable" :class="sortClasses('EarNum')" @click="flockStore.setSort('EarNum')">耳號</th><th class="sortable" :class="sortClasses('Breed')" @click="flockStore.setSort('Breed')">品種</th>
              <th class="sortable" :class="sortClasses('Sex')" @click="flockStore.setSort('Sex')">性別</th><th class="sortable" :class="sortClasses('BirthDate')" @click="flockStore.setSort('BirthDate')">出生日期</th>
              <th class="sortable" :class="sortClasses('status')" @click="flockStore.setSort('status')">狀態</th><th>操作</th>
          </tr></thead>
          <tbody>
            <tr v-if="flockStore.filteredAndSortedSheep.length === 0"><td colspan="6" class="no-data-message">尚無羊隻資料或無符合條件者。</td></tr>
            <tr v-for="sheep in flockStore.filteredAndSortedSheep" :key="sheep.id">
              <td>{{ sheep.EarNum }}</td><td>{{ sheep.Breed }}</td><td>{{ sheep.Sex }}</td><td>{{ sheep.BirthDate }}</td><td>{{ sheep.status }}</td>
              <td class="action-cell">
                <button @click="goToConsultation(sheep.EarNum)" class="action-button small consult">諮詢</button>
                <button @click="openModal(sheep.EarNum, 'basicInfoTab')" class="action-button small edit">編輯</button>
                <button @click="openModal(sheep.EarNum, 'eventsLogTab')" class="action-button small log">日誌</button>
                <button @click="handleDeleteSheep(sheep.EarNum)" class="action-button small delete">刪除</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
    <SheepModal v-if="isModalOpen" :ear-num="editingEarNum" :initial-tab="modalInitialTab" @close="closeModal" @sheep-updated="handleSheepUpdated"/>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useFlockStore } from '@/stores/flock';
import * as api from '@/services/api';
import Card from '@/components/Card.vue';
import SheepModal from '@/components/SheepModal.vue';

const flockStore = useFlockStore();
const router = useRouter();
const isModalOpen = ref(false);
const editingEarNum = ref(null);
const modalInitialTab = ref('basicInfoTab');

const sortClasses = (key) => ({ 'sort-asc': flockStore.sort.key === key && flockStore.sort.direction === 'asc', 'sort-desc': flockStore.sort.key === key && flockStore.sort.direction === 'desc' });

function openModal(earNum = null, tab = 'basicInfoTab') { editingEarNum.value = earNum; modalInitialTab.value = tab; isModalOpen.value = true; }
function closeModal() { isModalOpen.value = false; editingEarNum.value = null; }
async function handleSheepUpdated() { closeModal(); await flockStore.fetchSheep(); }
async function handleDeleteSheep(earNum) { if (confirm(`確定要刪除耳號為 ${earNum} 的羊隻嗎？`)) { try { await api.deleteSheep(earNum); await flockStore.fetchSheep(); } catch (error) { alert(`刪除失敗: ${error.message}`); } } }

// 【新增】跳轉到諮詢頁的方法
function goToConsultation(earNum) {
    router.push({ name: 'consultation', query: { earNum } });
}

onMounted(() => { if (flockStore.sheepCache.length === 0) flockStore.fetchSheep(); });
</script>

<style scoped>
h2 { font-size: 1.8em; color: #1e3a8a; margin-top: 0; margin-bottom: 25px; padding-bottom: 12px; border-bottom: 2px solid #d1d5db; }
.filter-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px 20px; margin-bottom: 20px; }
.filter-item label, .date-range label { font-size: 0.9em; font-weight: 500; margin-bottom: 6px; display: block; }
.filter-item input, .filter-item select { width: 100%; padding: 8px 10px; border-radius: 6px; border: 1px solid #d1d5db; }
.date-range div { display: flex; align-items: center; gap: 8px; }
.filter-actions { display: flex; justify-content: flex-end; }
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px; }
.list-summary { font-weight: 500; }
.loader-container { text-align: center; padding: 50px 0; }
.table-responsive { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 0.9em; }
th, td { border: 1px solid #e5e7eb; padding: 12px 15px; text-align: left; vertical-align: middle; white-space: nowrap; }
th { background-color: #f9fafb; font-weight: 600; position: relative; }
th.sortable { cursor: pointer; user-select: none; padding-right: 25px; }
th.sortable::after { content: '↕'; position: absolute; right: 8px; top: 50%; transform: translateY(-50%); color: #9ca3af; }
th.sortable.sort-asc::after { content: '↑'; color: #3b82f6; }
th.sortable.sort-desc::after { content: '↓'; color: #3b82f6; }
.no-data-message { text-align: center; padding: 20px; color: #6b7280; }
.action-cell { min-width: 230px; }
.action-button { background-color: #3b82f6; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.95em; font-weight: 500; }
.action-button.secondary-button { background-color: #6b7280; }
.action-button.small { font-size: 0.85em; padding: 7px 12px; margin-right: 5px; }
.action-button.edit   { background-color: #f59e0b; }
.action-button.delete { background-color: #ef4444; }
.action-button.consult{ background-color: #22c55e; }
.action-button.log    { background-color: #60a5fa; }
</style>
<!-- END OF FILE frontend/src/views/FlockView.vue -->