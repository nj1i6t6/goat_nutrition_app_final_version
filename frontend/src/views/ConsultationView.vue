<!-- START OF FILE frontend/src/views/ConsultationView.vue -->
<template>
  <div>
    <h2>飼養建議諮詢</h2>
    <Card>
      <form @submit.prevent="handleGetRecommendation">
        <div class="grid-layout-4">
          <div class="earnum-search-group">
            <label for="consult_ear_num">諮詢耳號:</label>
            <div class="input-with-button">
              <input type="text" id="consult_ear_num" v-model="formData.EarNum" @input="clearFetchedData" placeholder="手動輸入或從列表帶入">
              <button type="button" @click="fetchDataByEarNum()" class="action-button small">帶入</button>
            </div>
          </div>
          <div><label for="consult_specific_breed_name">品種:</label><input type="text" id="consult_specific_breed_name" v-model="formData.Breed"></div>
          <div><label for="consult_sex">性別:</label><input type="text" id="consult_sex" v-model="formData.Sex"></div>
          <div><label for="consult_birth_date">出生日期:</label><input type="date" id="consult_birth_date" :value="formatDateForInput(formData.BirthDate)" @input="formData.BirthDate = $event.target.value"></div>
          <div><label for="consult_body_weight_kg">體重(kg):</label><input type="number" id="consult_body_weight_kg" v-model.number="formData.Body_Weight_kg" step="0.1" required></div>
          <div><label for="consult_age_months">月齡:</label><input type="number" id="consult_age_months" v-model.number="formData.Age_Months" required></div>
        </div>
        <hr>
        <div><label for="consult_status">生理狀態:</label><select id="consult_status" v-model="formData.status" required>
            <option value="">請選擇...</option><option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">{{ opt.text }}</option>
        </select></div>
        <div v-if="dynamicInputs.length > 0" class="grid-layout-3" style="margin-top:15px;">
            <div v-for="input in dynamicInputs" :key="input.name">
                <label :for="'consult_' + input.name">{{ input.label }}:</label>
                <input :type="input.type" :id="'consult_' + input.name" v-model.number="formData[input.name]" :step="input.step" :placeholder="input.placeholder">
            </div>
        </div>
        <div><label for="consult_other_remarks">使用者備註(給AI):</label><textarea id="consult_other_remarks" v-model="formData.other_remarks"></textarea></div>
        <div style="margin-top:20px;">
          <!-- 【重要修正】:disabled 條件直接讀取 authStore.apiKey -->
          <button type="submit" class="action-button" :disabled="isLoading || !authStore.apiKey">
            {{ isLoading ? '分析中...' : '獲取建議' }}
          </button>
          <p v-if="!authStore.apiKey" class="form-note-error">請先在「系統設定」頁面設定有效的 API 金鑰。</p>
        </div>
      </form>
    </Card>
    
    <Card v-if="resultHtml || isLoading || error">
        <h3>💡 領頭羊博士的建議</h3>
        <div v-if="isLoading" class="loader-container"><div class="loader"></div></div>
        <div v-if="error" class="status-tag error">{{ error }}</div>
        <div v-if="resultHtml" class="markdown-content" v-html="resultHtml"></div>
    </Card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFlockStore } from '@/stores/flock'
import * as api from '@/services/api'
import Card from '@/components/Card.vue'

const authStore = useAuthStore()
const flockStore = useFlockStore()
const route = useRoute()
const router = useRouter()

const isLoading = ref(false)
const error = ref('')
const resultHtml = ref('')
const formData = reactive({})
const statusOptions = [
    {value:"maintenance",text:"維持期"}, {value:"growing_young",text:"生長前期"}, {value:"growing_finishing",text:"生長育肥期"},
    {value:"gestating_early",text:"懷孕早期"}, {value:"gestating_late",text:"懷孕晚期"}, {value:"lactating_early",text:"泌乳早期"},
    {value:"lactating_peak",text:"泌乳高峰期"}, {value:"lactating_mid",text:"泌乳中期"}, {value:"lactating_late",text:"泌乳晚期"}, {value:"dry_period",text:"乾乳期"}
];

const dynamicInputs = computed(() => {
    const inputs = []; const status = formData.status || '';
    if (status.includes('growing')) inputs.push({ name: 'target_average_daily_gain_g', label: '目標日增重(g/天)', type: 'number', placeholder: '150' });
    if (status.includes('lactating')) {
        inputs.push({ name: 'milk_yield_kg_day', label: '日產奶量(kg/天)', type: 'number', step: '0.1', placeholder: '3.5' });
        inputs.push({ name: 'milk_fat_percentage', label: '乳脂率(%)', type: 'number', step: '0.1', placeholder: '3.8' });
    }
    if (status.includes('gestating')) inputs.push({ name: 'number_of_fetuses', label: '胎兒數', type: 'number', placeholder: '2' });
    return inputs;
});

watch(() => formData.status, () => {
    if (!formData.status?.includes('growing')) delete formData.target_average_daily_gain_g;
    if (!formData.status?.includes('lactating')) { delete formData.milk_yield_kg_day; delete formData.milk_fat_percentage; }
    if (!formData.status?.includes('gestating')) delete formData.number_of_fetuses;
});

const formatDateForInput = (d) => d ? new Date(d.replace(/-/g, '/')).toISOString().split('T')[0] : '';
function clearFetchedData() {
  const earNum = formData.EarNum;
  Object.keys(formData).forEach(key => delete formData[key]);
  formData.EarNum = earNum;
}

async function fetchDataByEarNum(earNumToFetch = null) {
  const earNum = earNumToFetch || formData.EarNum;
  if (!earNum) { alert('請輸入耳號'); return; }
  const sheepData = flockStore.getSheepByEarNum(earNum);
  if (sheepData) {
    Object.assign(formData, sheepData);
  } else {
    alert(`在羊群中找不到耳號為 ${earNum} 的羊隻。`);
  }
}

async function handleGetRecommendation() {
    isLoading.value = true; error.value = ''; resultHtml.value = '';
    try {
        const result = await api.getRecommendation(authStore.apiKey, formData);
        resultHtml.value = result.recommendation_html;
    } catch (e) {
        error.value = `獲取建議失敗: ${e.message}`;
    } finally { isLoading.value = false; }
}

onMounted(() => {
    if (flockStore.sheepCache.length === 0) flockStore.fetchSheep();
    const queryEarNum = route.query.earNum;
    if (queryEarNum) {
        fetchDataByEarNum(queryEarNum);
        router.replace({ query: {} });
    }
});
</script>

<style scoped>
h2 { font-size: 1.8em; color: #1e3a8a; margin-top: 0; margin-bottom: 25px; padding-bottom: 12px; border-bottom: 2px solid #d1d5db; }
h3 { font-size: 1.4em; color: #1e40af; margin-top: 0; margin-bottom: 18px; }
.grid-layout-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px 20px; }
.grid-layout-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px 20px; }
hr { border: 0; height: 1px; background-color: #e5e7eb; margin: 20px 0; }
label { display: block; margin-bottom: 8px; font-weight: 500; color: #4b5563; }
input, select, textarea { width: 100%; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 6px; box-sizing: border-box; font-size: 0.95em; background-color: #f9fafb; margin-bottom: 10px;}
textarea { min-height: 80px; }
.earnum-search-group .input-with-button { display: flex; gap: 5px; }
.earnum-search-group .input-with-button input { flex-grow: 1; }
.action-button { background-color: #3b82f6; color: white; padding: 11px 22px; border: none; border-radius: 6px; cursor: pointer; font-size: 1em; font-weight: 500; }
.action-button.small { padding: 10px 12px; font-size: 0.9em; margin-bottom: 10px; }
.action-button:disabled { background-color: #93c5fd; cursor: not-allowed; }
.form-note-error { color: #b91c1c; font-size: 0.9em; margin-top: 10px; }
.loader-container { text-align: center; padding: 20px; }
.status-tag.error { background-color: #fee2e2; color: #991b1b; padding: 10px; border-radius: 6px; }
.markdown-content { line-height: 1.7; }
</style>
<style>
.markdown-content h1, .markdown-content h2, .markdown-content h3 { color: #1e3a8a; border-bottom: 1px solid #e5e7eb; padding-bottom: 5px; }
.markdown-content table { border-collapse: collapse; width: 100%; margin: 1em 0; }
.markdown-content th, .markdown-content td { border: 1px solid #d1d5db; padding: 8px 12px; }
.markdown-content th { background-color: #f9fafb; }
</style>
<!-- END OF FILE frontend/src/views/ConsultationView.vue -->