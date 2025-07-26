<!-- START OF FILE frontend/src/components/SheepModal.vue -->
<template>
    <Teleport to="body">
        <div v-if="isOpen" class="modal" @click.self="closeModal">
            <div class="modal-content">
                <button class="close-button" @click="closeModal" aria-label="關閉模態框">×</button>
                <h3 id="modalTitle">{{ modalTitle }}</h3>

                <div v-if="error" class="status-tag error">{{ error }}</div>
                
                <div v-if="isLoading" class="loader-container">
                    <div class="loader"></div>
                    <p>{{ loadingMessage }}</p>
                </div>

                <div v-else class="modal-main-container">
                    <div class="tabs">
                        <button class="tab-button" :class="{ active: currentTab === 'basicInfoTab' }" @click="switchTab('basicInfoTab')">基本資料</button>
                        <button class="tab-button" :class="{ active: currentTab === 'eventsLogTab' }" @click="switchTab('eventsLogTab')" :disabled="isNewSheep">事件日誌</button>
                        <button class="tab-button" :class="{ active: currentTab === 'historyTab' }" @click="switchTab('historyTab')" :disabled="isNewSheep">歷史數據</button>
                    </div>

                    <div class="modal-body">
                        <!-- 基本資料頁籤 -->
                        <div v-show="currentTab === 'basicInfoTab'" class="tab-content active">
                            <form @submit.prevent="handleSaveSheep">
                                <div class="record-date-section">
                                    <label for="record_date">本次更新/補登的記錄日期:</label>
                                    <input type="date" id="record_date" v-model="formData.record_date">
                                    <p>更新體重、產奶量等數據時，將以此日期存入歷史記錄。</p>
                                </div>
                                
                                <h4>核心識別資料</h4>
                                <div class="grid-layout-3">
                                    <div><label for="modal_EarNum">耳號 (EarNum):</label><input type="text" id="modal_EarNum" v-model="formData.EarNum" :disabled="!isNewSheep" required></div>
                                    <div><label for="modal_FarmNum">牧場編號 (FarmNum):</label><input type="text" id="modal_FarmNum" v-model="formData.FarmNum"></div>
                                    <div><label for="modal_RUni">唯一記錄編號 (RUni):</label><input type="text" id="modal_RUni" v-model="formData.RUni"></div>
                                </div>

                                <h4>基礎生理資料</h4>
                                <div class="grid-layout-3">
                                    <div><label for="modal_Sex">性別 (Sex):</label>
                                        <select id="modal_Sex" v-model="formData.Sex">
                                            <option value="">請選擇...</option>
                                            <option value="母">母</option>
                                            <option value="公">公</option>
                                            <option value="閹">閹</option>
                                        </select>
                                    </div>
                                    <div><label for="modal_BirthDate">出生日期 (BirthDate):</label><input type="date" id="modal_BirthDate" v-model="formData.BirthDate"></div>
                                    <div><label for="modal_BirWei">出生體重 (kg):</label><input type="number" id="modal_BirWei" v-model.number="formData.BirWei" step="0.1"></div>
                                </div>

                                <h4>血統資料</h4>
                                <div class="grid-layout-4">
                                     <div><label for="modal_Breed">品種 (Breed):</label><input type="text" id="modal_Breed" v-model="formData.Breed" placeholder="例如: 薩能"></div>
                                     <div><label for="modal_Sire">父號 (Sire):</label><input type="text" id="modal_Sire" v-model="formData.Sire"></div>
                                     <div><label for="modal_SireBre">父系品種 (SireBre):</label><input type="text" id="modal_SireBre" v-model="formData.SireBre"></div>
                                     <div><label for="modal_Dam">母號 (Dam):</label><input type="text" id="modal_Dam" v-model="formData.Dam"></div>
                                     <div><label for="modal_DamBre">母系品種 (DamBre):</label><input type="text" id="modal_DamBre" v-model="formData.DamBre"></div>
                                </div>
                                <hr>
                                
                                <h4>飼養管理資料</h4>
                                <div class="grid-layout-3">
                                    <div><label for="modal_breed_category">品種類別:</label>
                                        <select id="modal_breed_category" v-model="formData.breed_category">
                                            <option value="">請選擇...</option>
                                            <option value="Dairy">乳用</option>
                                            <option value="Meat">肉用</option>
                                            <option value="Fiber">毛用</option>
                                            <option value="DualPurpose">兼用</option>
                                        </select>
                                    </div>
                                    <div><label for="modal_Body_Weight_kg">體重 (公斤):</label><input type="number" id="modal_Body_Weight_kg" v-model.number="formData.Body_Weight_kg" step="0.1"></div>
                                    <div>
                                        <label>月齡 (自動計算):</label>
                                        <p class="auto-calc-field">{{ calculatedAge }}</p>
                                    </div>
                                    <div><label for="modal_status">生理狀態:</label>
                                        <select id="modal_status" v-model="formData.status">
                                          <option value="">請選擇...</option>
                                          <option value="maintenance">維持期</option>
                                          <option value="growing_young">生長前期</option>
                                          <option value="growing_finishing">生長育肥期</option>
                                          <option value="gestating_early">懷孕早期</option>
                                          <option value="gestating_late">懷孕晚期</option>
                                          <option value="lactating_early">泌乳早期</option>
                                          <option value="lactating_peak">泌乳高峰期</option>
                                          <option value="lactating_mid">泌乳中期</option>
                                          <option value="lactating_late">泌乳晚期</option>
                                          <option value="dry_period">乾乳期</option>
                                        </select>
                                    </div>
                                    <div><label for="modal_target_average_daily_gain_g">目標日增重 (克/天):</label><input type="number" id="modal_target_average_daily_gain_g" v-model.number="formData.target_average_daily_gain_g"></div>
                                    <div><label for="modal_activity_level">活動量:</label>
                                        <select id="modal_activity_level" v-model="formData.activity_level">
                                          <option value="">未指定</option>
                                          <option value="confined">舍飼</option>
                                          <option value="grazing_flat_pasture">平地放牧</option>
                                        </select>
                                    </div>
                                </div>

                                <h4>生產與繁殖資料</h4>
                                <div class="grid-layout-3">
                                    <div :class="{ 'disabled-field': !isFemale }"><label for="modal_milk_yield_kg_day">日產奶量 (公斤/天):</label><input type="number" id="modal_milk_yield_kg_day" v-model.number="formData.milk_yield_kg_day" step="0.1" :disabled="!isFemale"></div>
                                    <div :class="{ 'disabled-field': !isFemale }"><label for="modal_milk_fat_percentage">乳脂率 (%):</label><input type="number" id="modal_milk_fat_percentage" v-model.number="formData.milk_fat_percentage" step="0.1" :disabled="!isFemale"></div>
                                    <div :class="{ 'disabled-field': !isFemale }"><label for="modal_number_of_fetuses">懷胎數:</label><input type="number" id="modal_number_of_fetuses" v-model.number="formData.number_of_fetuses" :disabled="!isFemale"></div>
                                    <div><label for="modal_Lactation">泌乳胎次 (Lactation):</label><input type="number" id="modal_Lactation" v-model.number="formData.Lactation"></div>
                                    <div><label for="modal_LittleSize">產仔數/窩 (LittleSize):</label><input type="number" id="modal_LittleSize" v-model.number="formData.LittleSize"></div>
                                </div>

                                <h4>牧場管理記錄</h4>
                                 <div class="grid-layout-3">
                                    <div><label for="modal_ManaClas">管理分類 (ManaClas):</label><input type="text" id="modal_ManaClas" v-model="formData.ManaClas"></div>
                                    <div><label for="modal_Class">等級 (Class):</label><input type="text" id="modal_Class" v-model="formData.Class"></div>
                                    <div><label for="modal_MoveDate">異動日期 (MoveDate):</label><input type="date" id="modal_MoveDate" v-model="formData.MoveDate"></div>
                                    <div class="full-width-field"><label for="modal_MoveCau">異動原因 (MoveCau):</label><input type="text" id="modal_MoveCau" v-model="formData.MoveCau"></div>
                                 </div>
                                 <hr>

                                <h4>代理人備註與提醒日期</h4>
                                <div class="grid-layout-3">
                                    <div class="full-width-field"><label for="modal_agent_notes">代理人備註 (內部觀察):</label><textarea id="modal_agent_notes" v-model="formData.agent_notes"></textarea></div>
                                    <div><label for="modal_next_vaccination_due_date">下次疫苗日期:</label><input type="date" id="modal_next_vaccination_due_date" v-model="formData.next_vaccination_due_date"></div>
                                    <div><label for="modal_next_deworming_due_date">下次驅蟲日期:</label><input type="date" id="modal_next_deworming_due_date" v-model="formData.next_deworming_due_date"></div>
                                    <div :class="{ 'disabled-field': !isFemale }"><label for="modal_expected_lambing_date">預計產仔日期:</label><input type="date" id="modal_expected_lambing_date" v-model="formData.expected_lambing_date" :disabled="!isFemale"></div>
                                </div>
                                <button type="submit" class="action-button form-submit-button" :disabled="isSaving">
                                  {{ isSaving ? '儲存中...' : '儲存羊隻資料' }}
                                </button>
                            </form>
                        </div>
                        
                        <div v-show="currentTab === 'eventsLogTab'" class="tab-content active">
                            <h4>{{ currentEarNum }} 的事件日誌</h4>
                            <form @submit.prevent="handleSaveEvent">
                                <div class="grid-layout-3" style="align-items: flex-end;">
                                    <div><label for="event_date">事件日期:</label><input type="date" id="event_date" v-model="eventForm.event_date" required></div>
                                    <div><label for="event_type">事件類型:</label>
                                        <select id="event_type" v-model="eventForm.event_type" required>
                                            <option value="">請選擇...</option>
                                            <option v-for="opt in eventOptions" :key="opt.id" :value="opt.name">{{ opt.name }}</option>
                                        </select>
                                    </div>
                                    <div><label for="event_description">簡要描述:</label>
                                        <input type="text" id="event_description" v-model="eventForm.description" list="event_description_datalist" placeholder="選擇類型後載入建議">
                                        <datalist id="event_description_datalist">
                                          <option v-for="desc in eventDescriptionOptions" :key="desc.id" :value="desc.description"></option>
                                        </datalist>
                                    </div>
                                </div>
                                <div style="margin-top:15px;"><label for="event_notes">詳細備註:</label><textarea id="event_notes" v-model="eventForm.notes"></textarea></div>
                                <button type="submit" class="action-button" style="margin-top:15px;" :disabled="isSaving">
                                    {{ isEditingEvent ? '更新此事件' : '新增此事件' }}
                                </button>
                                <button type="button" v-if="isEditingEvent" @click="resetEventForm" class="action-button secondary-button">取消編輯</button>
                            </form>
                            <hr>
                            <div class="table-container">
                                <table v-if="events.length > 0">
                                    <thead><tr><th>日期</th><th>類型</th><th>描述</th><th>備註</th><th>操作</th></tr></thead>
                                    <tbody>
                                        <tr v-for="event in events" :key="event.id">
                                            <td>{{ formatDateForInput(event.event_date) }}</td>
                                            <td>{{ event.event_type }}</td>
                                            <td>{{ event.description }}</td>
                                            <td class="notes-cell">{{ event.notes }}</td>
                                            <td>
                                                <button @click="editEvent(event)" class="action-button small edit">編輯</button>
                                                <button @click="deleteEvent(event.id)" class="action-button small delete">刪除</button>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                                <p v-else class="status-tag neutral">此羊隻尚無事件記錄。</p>
                            </div>
                        </div>

                        <div v-show="currentTab === 'historyTab'" class="tab-content active">
                            <h4>{{ currentEarNum }} 的歷史數據</h4>
                            <p class="form-note">此處的數據是您在「基本資料」頁面更新體重、產奶量等數值時自動生成的記錄。</p>
                            <hr>
                            <div class="grid-layout-history">
                                <div class="table-container">
                                    <table v-if="history.length > 0">
                                        <thead><tr><th>記錄日期</th><th>類型</th><th>數值</th><th>操作</th></tr></thead>
                                        <tbody>
                                            <tr v-for="rec in history" :key="rec.id">
                                                <td>{{ formatDateForInput(rec.record_date) }}</td>
                                                <td>{{ historyTypeMap[rec.record_type] || rec.record_type }}</td>
                                                <td>{{ rec.value }}</td>
                                                <td><button @click="deleteHistory(rec.id)" class="action-button small delete">刪除</button></td>
                                            </tr>
                                        </tbody>
                                    </table>
                                    <p v-else class="status-tag neutral">此羊隻尚無歷史數據記錄。</p>
                                </div>
                                <div class="chart-container">
                                  <canvas ref="historyChartCanvas"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </Teleport>
</template>

<script setup>
import { ref, computed, watch, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import * as api from '@/services/api'
import Chart from 'chart.js/auto'
import { enUS } from 'date-fns/locale'
import 'chartjs-adapter-date-fns';

const props = defineProps({ earNum: { type: String, default: null }, initialTab: { type: String, default: 'basicInfoTab' }});
const emit = defineEmits(['close', 'sheep-updated']);

const getTodayDateString = () => new Date(new Date().getTime() - new Date().getTimezoneOffset() * 60000).toISOString().split('T')[0];
const formatDateForInput = (d) => d ? new Date(d.replace(/-/g, '/')).toISOString().split('T')[0] : '';

const isOpen = ref(true);
const currentTab = ref(props.initialTab);
const isLoading = ref(true);
const isSaving = ref(false);
const loadingMessage = ref('載入資料中...');
const error = ref('');
const currentEarNum = ref(props.earNum);

const formData = reactive({ record_date: getTodayDateString() });
const eventForm = reactive({ event_date: getTodayDateString(), event_type: '', description: '', notes: '' });
const isEditingEvent = ref(false);

const events = ref([]);
const eventOptions = ref([]);

const history = ref([]);
const historyChartCanvas = ref(null);
let chartInstance = null;

const historyTypeMap = { 'Body_Weight_kg': '體重(kg)', 'milk_yield_kg_day': '日產奶量(kg/天)', 'milk_fat_percentage': '乳脂率(%)' };

const modalTitle = computed(() => isNewSheep.value ? '新增羊隻資料' : `管理羊隻資料 (耳號: ${currentEarNum.value})`);
const isNewSheep = computed(() => !props.earNum);
const calculatedAge = computed(() => {
    if (!formData.BirthDate) { formData.Age_Months = null; return '-'; }
    const birthDate = new Date(formData.BirthDate);
    if (isNaN(birthDate.getTime())) { formData.Age_Months = null; return '-'; }
    const totalMonths = (new Date().getFullYear() - birthDate.getFullYear()) * 12 + (new Date().getMonth() - birthDate.getMonth());
    formData.Age_Months = totalMonths;
    return `${totalMonths} 個月`;
});
const isFemale = computed(() => formData.Sex === '母');
const eventDescriptionOptions = computed(() => {
    const selectedType = eventOptions.value.find(opt => opt.name === eventForm.event_type);
    return selectedType ? selectedType.descriptions : [];
});

const closeModal = () => { isOpen.value = false; emit('close'); };

const switchTab = async (tabName) => {
    if (isNewSheep.value && tabName !== 'basicInfoTab') return;
    currentTab.value = tabName;
    if (tabName === 'eventsLogTab' && events.value.length === 0) await fetchEvents();
    if (tabName === 'historyTab' && history.value.length === 0) await fetchHistory();
};

const fetchSheepData = async () => {
    if (isNewSheep.value) { isLoading.value = false; return; }
    isLoading.value = true; error.value = '';
    try {
        const data = await api.getSheepDetails(props.earNum);
        Object.keys(formData).forEach(key => delete formData[key]); // 清空舊數據
        Object.assign(formData, { record_date: getTodayDateString() }); // 重設 record_date
        Object.keys(data).forEach(key => formData[key] = (key.includes('Date') || key.includes('date')) ? formatDateForInput(data[key]) : data[key]);
    } catch (e) { error.value = `載入羊隻資料失敗: ${e.message}`; } 
    finally { isLoading.value = false; }
};

async function handleSaveSheep() {
    isSaving.value = true;
    error.value = '';
    try {
        if (isNewSheep.value) {
            // 新增模式
            const result = await api.addSheep(formData);
            // 【重要修正】新增成功後，不要自己更新狀態，而是直接發出事件讓父元件刷新整個列表
            // 這樣可以確保所有數據都是從後端獲取的最新、最完整的狀態
            emit('sheep-updated');
        } else {
            // 更新模式
            await api.updateSheep(props.earNum, formData);
            emit('sheep-updated');
        }
    } catch (e) {
        error.value = `儲存失敗: ${e.message}`;
    } finally {
        isSaving.value = false;
    }
}

const fetchEvents = async () => { try { events.value = await api.getSheepEvents(currentEarNum.value); } catch (e) { error.value = `載入事件失敗: ${e.message}`; }};
const fetchEventOptions = async () => { try { eventOptions.value = await api.getEventOptions(); } catch (e) { console.error("無法獲取事件選項:", e); }};
const resetEventForm = () => { Object.assign(eventForm, { id: null, event_date: getTodayDateString(), event_type: '', description: '', notes: '' }); isEditingEvent.value = false; };
const editEvent = (event) => { Object.assign(eventForm, event, { event_date: formatDateForInput(event.event_date) }); isEditingEvent.value = true; };
const handleSaveEvent = async () => {
    isSaving.value = true; error.value = '';
    try {
        const dataToSave = { ...eventForm };
        if (isEditingEvent.value) {
            await api.updateSheepEvent(dataToSave.id, dataToSave);
        } else {
            await api.addSheepEvent(currentEarNum.value, dataToSave);
        }
        resetEventForm();
        await fetchEvents();
    } catch (e) { error.value = `儲存事件失敗: ${e.message}`; } 
    finally { isSaving.value = false; }
};
const deleteEvent = async (id) => { if (confirm('確定刪除此事件?')) { try { await api.deleteSheepEvent(id); await fetchEvents(); } catch (e) { error.value = `刪除事件失敗: ${e.message}`; }}};

const fetchHistory = async () => {
    try {
        history.value = await api.getSheepHistory(currentEarNum.value);
        await nextTick();
        renderChart();
    } catch (e) { error.value = `載入歷史數據失敗: ${e.message}`; }
};
const deleteHistory = async (id) => { if (confirm('確定刪除此歷史記錄?')) { try { await api.deleteSheepHistory(id); await fetchHistory(); } catch (e) { error.value = `刪除歷史記錄失敗: ${e.message}`; }}};

const renderChart = () => {
    if (chartInstance) chartInstance.destroy();
    if (!historyChartCanvas.value || history.value.length === 0) return;
    const dataByType = history.value.reduce((acc, curr) => { (acc[curr.record_type] = acc[curr.record_type] || []).push({ x: curr.record_date, y: curr.value }); return acc; }, {});
    const datasets = Object.keys(dataByType).map((type, i) => ({ label: historyTypeMap[type] || type, data: dataByType[type], borderColor: ['#3b82f6', '#10b981', '#f59e0b'][i % 3], tension: 0.1 }));
    chartInstance = new Chart(historyChartCanvas.value.getContext('2d'), { type: 'line', data: { datasets }, options: { responsive: true, maintainAspectRatio: false, scales: { x: { type: 'time', time: { unit: 'day' }, adapter: { locale: enUS } } } }});
};

watch(isFemale, (is) => { if (!is) { formData.milk_yield_kg_day = null; formData.milk_fat_percentage = null; formData.number_of_fetuses = null; formData.expected_lambing_date = null; }});
watch(currentTab, (tab) => { if (tab === 'historyTab') nextTick(renderChart); });

onMounted(() => {
    fetchSheepData();
    if (!isNewSheep.value) fetchEventOptions();
    const handleKeydown = (e) => { if (e.key === 'Escape') closeModal(); };
    window.addEventListener('keydown', handleKeydown);
    onUnmounted(() => window.removeEventListener('keydown', handleKeydown));
});
</script>


<style scoped>
.modal {
    position: fixed; z-index: 1050; left: 0; top: 0; width: 100%; height: 100%;
    overflow: hidden; background-color: rgba(0,0,0,0.6);
    display: flex; align-items: center; justify-content: center;
}
.modal-content {
    background-color: #ffffff; margin: auto; padding: 30px; border: none;
    width: 90%; max-width: 950px; border-radius: 10px; position: relative;
    box-shadow: 0 8px 25px rgba(0,0,0,0.15); display: flex; flex-direction: column;
    max-height: 90vh;
}
.modal-main-container {
    display: flex; flex-direction: column; min-height: 0;
}
.modal-content h3 {
    text-align: center; color: #1e3a8a; margin-top: 0; margin-bottom: 25px; font-size: 1.6em;
}
.modal-body {
    overflow-y: auto; padding-right: 15px; flex-grow: 1;
}
.close-button {
    color: #9ca3af; background: none; border: none; font-size: 1.8em; font-weight: bold;
    position: absolute; top: 15px; right: 20px; transition: color 0.2s; cursor: pointer;
}
.close-button:hover { color: #374151; }
hr { border: 0; height: 1px; background-color: #e5e7eb; margin: 25px 0; }
.tabs { display: flex; border-bottom: 1px solid #e5e7eb; margin-bottom: 25px; flex-shrink: 0;}
.tab-button {
    background: none; border: none; padding: 14px 20px; cursor: pointer; font-size: 1.05em;
    color: #6b7280; border-bottom: 3px solid transparent; margin-bottom: -1px;
    transition: color 0.2s, border-color 0.2s;
}
.tab-button.active { color: #3b82f6; border-bottom-color: #3b82f6; font-weight: 600; }
.tab-button:disabled { color: #9ca3af; cursor: not-allowed; border-bottom-color: transparent; }
.tab-content.active { display: block; }

.loader-container { text-align: center; padding: 50px 0; }
.status-tag.error {
    background-color: #fee2e2; color: #991b1b; padding: 10px; border-radius: 6px;
    margin-bottom: 15px; text-align: center;
}
.record-date-section {
    background: #eef2ff; padding: 15px; border-radius: 6px; margin-bottom: 20px;
}
.record-date-section label { font-weight:bold; color:#4338ca; }
.record-date-section p { font-size:0.85em; color:#4f46e5; margin-top:5px; margin-bottom:0; }
h4 { font-size: 1.15em; color: #374151; margin-top: 20px; margin-bottom: 12px; }
.grid-layout-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px 20px; }
.grid-layout-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px 20px; }
.full-width-field { grid-column: 1 / -1; }

label { display: block; margin-bottom: 8px; font-weight: 500; color: #4b5563; }
input, select, textarea {
    width: 100%; padding: 10px 12px; border: 1px solid #d1d5db;
    border-radius: 6px; box-sizing: border-box; font-size: 0.95em;
    background-color: #f9fafb;
}
textarea { min-height: 80px; resize: vertical; }
.auto-calc-field {
    padding: 10px 12px; background-color: #f3f4f6; border-radius: 6px;
    margin: 0; min-height: 21px; font-size: 0.95em; color: #4b5563;
}
.disabled-field { opacity: 0.6; }
.disabled-field label { color: #9ca3af; }
.disabled-field input, .disabled-field select { background-color: #f3f4f6; cursor: not-allowed; }

.action-button {
    background-color: #3b82f6; color: white; padding: 11px 22px;
    border: none; border-radius: 6px; cursor: pointer;
    font-size: 1em; font-weight: 500; transition: background-color 0.2s ease;
}
.action-button:disabled { background-color: #93c5fd; cursor: not-allowed; }
.form-submit-button { margin-top: 20px; }
.secondary-button { background-color: #6b7280; margin-left: 10px; }
.action-button.small { font-size: 0.8em; padding: 5px 10px; margin: 0 2px; }
.action-button.edit { background-color: #f59e0b; }
.action-button.delete { background-color: #ef4444; }

.table-container { max-height: 300px; overflow-y: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 8px 12px; border: 1px solid #e5e7eb; text-align: left; vertical-align: middle;}
th { background-color: #f9fafb; font-weight: 600; position: sticky; top: 0; }
.notes-cell { white-space: pre-wrap; max-width: 200px; }
.status-tag.neutral { background-color: #e5e7eb; color: #4b5563; padding: 10px; text-align:center; display: block; }
.form-note { font-size:0.9em; color:#64748b; }
.grid-layout-history { display: grid; grid-template-columns: 1fr 1.5fr; gap: 20px; align-items: start; }
.chart-container { position: relative; height: 350px; }
</style>
<!-- END OF FILE frontend/src/components/SheepModal.vue -->