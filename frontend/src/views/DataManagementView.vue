<!-- START OF FILE frontend/src/views/DataManagementView.vue -->
<template>
  <div>
    <h2>數據管理中心</h2>
    <Card>
      <h3>資料匯出</h3>
      <p>將您帳戶中所有的羊隻基礎資料、事件日誌、歷史數據及 AI 聊天記錄備份為一份完整的 Excel (.xlsx) 檔案。</p>
      <button @click="handleExport" class="action-button" :disabled="isExporting">
        <span v-if="isExporting" class="loader small"></span>
        {{ isExporting ? '匯出中...' : '匯出全部資料' }}
      </button>
      <div v-if="exportStatus" class="status-message" :class="exportStatus.type">{{ exportStatus.message }}</div>
    </Card>

    <h3 style="margin-top: 30px;">資料導入</h3>
    <div class="tabs">
        <button class="tab-button" :class="{ active: currentTab === 'default' }" @click="switchTab('default')">快速導入 (標準範本)</button>
        <button class="tab-button" :class="{ active: currentTab === 'custom' }" @click="switchTab('custom')">自訂導入</button>
    </div>

    <Card>
        <div v-if="currentTab === 'default'">
            <h4>步驟一：下載並填寫標準範本</h4>
            <p>請下載系統提供的標準 Excel 範本，並將您的數據按照範本的格式填寫。</p>
            <a href="/download_template" class="action-button" download>下載標準範本</a>
            <hr>
            <h4>步驟二：上傳已填寫的範本檔案</h4>
            <input type="file" @change="handleFileChange($event, 'default')" ref="defaultFileInput" style="display:none" accept=".xlsx,.xls">
            <button @click="defaultFileInput.click()" class="action-button">選擇檔案</button>
            <p v-if="defaultFile" class="file-name-display">{{ defaultFile.name }}</p>
            <hr>
            <h4>步驟三：執行導入</h4>
            <button @click="handleProcessImport('default')" class="action-button consult" :disabled="!defaultFile || isImporting">
                {{ isImporting ? '導入中...' : '執行快速導入' }}
            </button>
        </div>
        <div v-if="currentTab === 'custom'">
            <h4>步驟一：上傳您的 Excel 檔案</h4>
            <input type="file" @change="handleFileChange($event, 'custom')" ref="customFileInput" style="display:none" accept=".xlsx,.xls">
            <button @click="customFileInput.click()" class="action-button">選擇檔案</button>
            <div v-if="isAnalyzing" class="loader-container"><div class="loader"></div>分析中...</div>
            <p v-if="customFile && !analyzedData" class="file-name-display">{{ customFile.name }}</p>

            <div v-if="analyzedData" style="margin-top: 20px;">
                <hr>
                <h4>步驟二：設定工作表用途與欄位映射</h4>
                <div class="sheet-analysis-container">
                    <div v-for="(sheet, sheetName) in analyzedData" :key="sheetName" class="sheet-item">
                        <div class="sheet-header">
                            <h5>工作表: {{ sheetName }}</h5>
                            <span>(共 {{ sheet.rows }} 筆資料)</span>
                        </div>
                         <div class="table-responsive">
                            <table class="mini-table">
                                <thead><tr><th v-for="col in sheet.columns" :key="col">{{ col }}</th></tr></thead>
                                <tbody><tr v-for="(row, i) in sheet.preview" :key="i">
                                    <td v-for="col in sheet.columns" :key="col">{{ row[col] }}</td>
                                </tr></tbody>
                            </table>
                        </div>
                        <div class="purpose-selection-area">
                            <label :for="'purpose-' + sheetName">用途:</label>
                            <select :id="'purpose-' + sheetName" v-model="mappingConfig[sheetName].purpose">
                                <option v-for="opt in sheetPurposeOptions" :key="opt.value" :value="opt.value">{{ opt.text }}</option>
                            </select>
                        </div>
                        <div v-if="systemFieldMappings[mappingConfig[sheetName].purpose]" class="column-mapping-area">
                            <div v-for="sysField in systemFieldMappings[mappingConfig[sheetName].purpose]" :key="sysField.key" class="mapping-row">
                                <div class="system-field">
                                    <label>{{ sysField.label }} <span v-if="sysField.required" style="color:red">*</span></label>
                                    <span class="field-example">範例: {{ sysField.example }}</span>
                                </div>
                                <div class="user-field">
                                    <select v-model="mappingConfig[sheetName].columns[sysField.key]">
                                        <option value="">-- 請選擇您的欄位 --</option>
                                        <option v-for="col in sheet.columns" :key="col" :value="col">{{ col }}</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <hr>
                <h4>步驟三：執行導入</h4>
                <button @click="handleProcessImport('custom')" class="action-button consult" :disabled="isImporting">
                     {{ isImporting ? '導入中...' : '執行自訂導入' }}
                </button>
            </div>
        </div>

        <div v-if="importResult" style="margin-top: 20px;">
            <h4>導入報告</h4>
            <div class="status-message" :class="importResult.success ? 'success' : 'error'">{{ importResult.message }}</div>
            <ul v-if="importResult.details && importResult.details.length > 0" class="import-details-list">
                <li v-for="(detail, i) in importResult.details" :key="i"><strong>{{ detail.sheet }}</strong>: {{ detail.message }}</li>
            </ul>
        </div>
    </Card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useFlockStore } from '@/stores/flock';
import { useDashboardStore } from '@/stores/dashboard'; // 【新增】導入 dashboard store
import * as api from '@/services/api';
import Card from '@/components/Card.vue';
import { sheetPurposeOptions, systemFieldMappings } from './dataManagementOptions';

const flockStore = useFlockStore();
const dashboardStore = useDashboardStore(); // 【新增】獲取 dashboard store 實例

const isExporting = ref(false);
const exportStatus = ref(null);
const isImporting = ref(false);
const importResult = ref(null);
const isAnalyzing = ref(false);

const currentTab = ref('default');
const defaultFile = ref(null);
const defaultFileInput = ref(null);
const customFile = ref(null);
const customFileInput = ref(null);
const analyzedData = ref(null);

const mappingConfig = reactive({});


async function handleExport() {
    isExporting.value = true;
    exportStatus.value = { type: 'info', message: '正在產生檔案...' };
    try {
        const response = await fetch('/api/data/export_excel');
        if (!response.ok) throw new Error('匯出失敗');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        const disposition = response.headers.get('content-disposition');
        const filename = disposition?.split('filename=')[1]?.replaceAll('"', '') || 'goat_data_export.xlsx';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        exportStatus.value = { type: 'success', message: '檔案匯出成功！' };
    } catch (e) {
        exportStatus.value = { type: 'error', message: `匯出失敗: ${e.message}` };
    } finally {
        isExporting.value = false;
    }
}

function handleFileChange(event, mode) {
    const file = event.target.files[0];
    if (!file) return;
    importResult.value = null;
    if (mode === 'default') {
        defaultFile.value = file;
        customFile.value = null;
        analyzedData.value = null;
    } else {
        customFile.value = file;
        defaultFile.value = null;
        analyzeFile();
    }
}

async function analyzeFile() {
    if (!customFile.value) return;
    isAnalyzing.value = true;
    analyzedData.value = null;
    Object.keys(mappingConfig).forEach(key => delete mappingConfig[key]);

    try {
        const result = await api.analyzeExcel(customFile.value);
        analyzedData.value = result.sheets;
        for (const sheetName in result.sheets) {
            mappingConfig[sheetName] = { purpose: '', columns: {} };
            const sheetColumns = result.sheets[sheetName].columns;
            for(const purposeKey in systemFieldMappings){
                const sysFields = systemFieldMappings[purposeKey];
                let matchCount = 0;
                let potentialMappings = {};
                sysFields.forEach(sf => {
                    const sysKeyLower = sf.key.toLowerCase().replace(/_/g, '');
                    const found = sheetColumns.find(userCol => userCol.toLowerCase().replace(/_/g, '') === sysKeyLower);
                    if(found){
                        matchCount++;
                        potentialMappings[sf.key] = found;
                    }
                });
                if(matchCount / sysFields.length > 0.5){
                    mappingConfig[sheetName].purpose = purposeKey;
                    mappingConfig[sheetName].columns = potentialMappings;
                    break;
                }
            }
        }
    } catch(e) {
        importResult.value = { success: false, message: `分析檔案失敗: ${e.message}` };
    } finally {
        isAnalyzing.value = false;
    }
}

async function handleProcessImport(mode) {
    const isDefault = mode === 'default';
    const file = isDefault ? defaultFile.value : customFile.value;
    if (!file) return;

    isImporting.value = true;
    importResult.value = null;

    let finalConfig = {};
    if (!isDefault) {
        finalConfig.sheets = {};
        for(const sheetName in mappingConfig) {
            if (mappingConfig[sheetName].purpose && mappingConfig[sheetName].purpose !== 'ignore') {
                finalConfig.sheets[sheetName] = mappingConfig[sheetName];
            }
        }
    }

    try {
        const result = await api.processImport(file, isDefault, finalConfig);
        importResult.value = result;
        if (result.success) {
            // 【修正】同時刷新兩個 store
            await flockStore.fetchSheep();
            await dashboardStore.forceRefreshDashboardData();
        }
    } catch(e) {
        importResult.value = { success: false, message: `導入失敗: ${e.message}` };
    } finally {
        isImporting.value = false;
    }
}

function switchTab(tabName) {
    currentTab.value = tabName;
    defaultFile.value = null;
    customFile.value = null;
    analyzedData.value = null;
    importResult.value = null;
}
</script>

<style scoped>
h2 { font-size: 1.8em; color: #1e3a8a; margin-top: 0; margin-bottom: 25px; padding-bottom: 12px; border-bottom: 2px solid #d1d5db; }
h3 { font-size: 1.4em; color: #1e40af; margin-top: 0; margin-bottom: 18px; }
h4 { font-size: 1.2em; color: #1e3a8a; margin-top: 25px; }
h5 { margin: 0; font-size: 1.1em; color: #374151;}
.action-button { background-color: #3b82f6; color: white; padding: 11px 22px; border: none; border-radius: 6px; cursor: pointer; font-size: 1em; font-weight: 500; display: inline-flex; align-items: center; gap: 8px; }
.action-button:disabled { background-color: #93c5fd; cursor: not-allowed; }
.action-button.consult { background-color: #16a34a; }
.loader.small { width: 15px; height: 15px; border-width: 2px; margin: 0; }
.loader-container { padding: 20px; text-align: center; }
.status-message { margin-top: 15px; padding: 12px; border-radius: 6px; font-weight: 500; }
.status-message.info { background-color: #dbeafe; color: #1e40af; }
.status-message.success { background-color: #dcfce7; color: #166534; }
.status-message.error { background-color: #fee2e2; color: #991b1b; }
.tabs { display: flex; border-bottom: 1px solid #d1d5db; margin-bottom: -1px; }
.tab-button { background: #f9fafb; border: 1px solid #d1d5db; border-bottom: none; padding: 12px 18px; cursor: pointer; font-size: 1em; color: #6b7280; border-radius: 6px 6px 0 0; margin-right: 5px;}
.tab-button.active { background: white; color: #3b82f6; font-weight: 600; border-bottom: 1px solid white; }
hr { border: 0; height: 1px; background-color: #e5e7eb; margin: 20px 0; }
.file-name-display { font-weight: 500; color: #166534; margin-top: 10px; }
.import-details-list { list-style-type: disc; padding-left: 20px; }
.sheet-analysis-container { display: flex; flex-direction: column; gap: 20px; }
.sheet-item { border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; }
.sheet-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.sheet-header span { font-size: 0.9em; color: #6b7280; }
.table-responsive { max-height: 150px; overflow: auto; margin-bottom: 15px; }
.mini-table { font-size: 0.8em; width: 100%; border-collapse: collapse; }
.mini-table th, .mini-table td { padding: 6px 8px; border: 1px solid #e5e7eb; white-space: nowrap; }
.purpose-selection-area { margin-bottom: 15px; }
.column-mapping-area { border-top: 1px dashed #d1d5db; padding-top: 15px; }
.mapping-row { display: flex; align-items: center; gap: 15px; margin-bottom: 12px; background-color: #f9fafb; padding: 10px; border-radius: 6px; }
.system-field { flex-basis: 40%; }
.system-field label { margin-bottom: 2px; font-weight: 500; }
.field-example { font-size: 0.8em; color: #6b7280; }
.user-field { flex-basis: 60%; }
select { width: 100%; padding: 8px 10px; border-radius: 6px; border: 1px solid #d1d5db; }
</style>
<!-- END OF FILE frontend/src/views/DataManagementView.vue -->