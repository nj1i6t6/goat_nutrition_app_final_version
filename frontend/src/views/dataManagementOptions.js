// --- START OF FILE frontend/src/views/dataManagementOptions.js ---

export const sheetPurposeOptions = [
    { value: "", text: "請選擇此工作表的用途..." },
    { value: "ignore", text: "忽略此工作表" },
    { value: "basic_info", text: "羊隻基礎資料" },
    { value: "kidding_record", text: "分娩記錄" },
    { value: "mating_record", text: "配種記錄" },
    { value: "yean_record", text: "泌乳/乾乳記錄" },
    { value: "weight_record", text: "體重記錄" },
    { value: "milk_yield_record", text: "產乳量記錄" },
    { value: "milk_analysis_record", text: "乳成分分析記錄" },
    { value: "breed_mapping", text: "品種代碼對照表" },
    { value: "sex_mapping", text: "性別代碼對照表" },
];

export const systemFieldMappings = {
    basic_info: [
        { key: "EarNum", label: "耳號", required: true, example: "0009AL088089" },
        { key: "Breed", label: "品種 (代碼)", example: "AL" },
        { key: "Sex", label: "性別 (代碼)", example: "1" },
        { key: "BirthDate", label: "出生日期", example: "2008/7/23" },
        { key: "Sire", label: "父號", example: "父羊耳號" },
        { key: "Dam", label: "母號", example: "母羊耳號" },
        { key: "BirWei", label: "出生體重(kg)", example: "3.5" },
        { key: "FarmNum", label: "牧場編號", example: "0009" },
    ],
    kidding_record: [
        { key: "EarNum", label: "母羊耳號", required: true, example: "0009AL077032" },
        { key: "YeanDate", label: "分娩日期", required: true, example: "2009/4/19" },
        { key: "KidNum", label: "仔羊耳號", example: "0009AL099027" },
    ],
    mating_record: [
        { key: "EarNum", label: "母羊耳號", required: true, example: "0009FX10K706" },
        { key: "Mat_date", label: "配種日期", required: true, example: "2012/1/18" },
        { key: "Mat_grouM_Sire", label: "配種公羊耳號", example: "0009AL070351" },
    ],
    yean_record: [
        { key: "EarNum", label: "母羊耳號", required: true, example: "0009FX10K706" },
        { key: "YeanDate", label: "泌乳開始日期", required: true, example: "2012/6/12" },
        { key: "DryOffDate", label: "乾乳日期", example: "1900/1/1" },
        { key: "Lactation", label: "泌乳胎次", example: "2" },
    ],
    weight_record: [
        { key: "EarNum", label: "耳號", required: true, example: "0007NU15..." },
        { key: "MeaDate", label: "測量日期", required: true, example: "2015/8/11" },
        { key: "Weight", label: "體重 (公斤)", required: true, example: "27.2" },
    ],
    milk_yield_record: [
        { key: "EarNum", label: "耳號", required: true, example: "0009AL071268" },
        { key: "MeaDate", label: "測量日期", required: true, example: "2010/11/10" },
        { key: "Milk", label: "產乳量 (公斤)", required: true, example: "4.1" },
    ],
    milk_analysis_record: [
        { key: "EarNum", label: "耳號", required: true, example: "0009AL077032" },
        { key: "MeaDate", label: "測量日期", required: true, example: "2019/1/1" },
        { key: "AMFat", label: "乳脂率 (%)", example: "3.29" },
    ],
    breed_mapping: [
        { key: "Code", label: "品種代碼", required: true, example: "AL" },
        { key: "Name", label: "品種全名", required: true, example: "阿爾拜因" },
    ],
    sex_mapping: [
        { key: "Code", label: "性別代碼", required: true, example: "2" },
        { key: "Name", label: "性別全名", required: true, example: "母" },
    ],
};

// --- END OF FILE frontend/src/views/dataManagementOptions.js ---