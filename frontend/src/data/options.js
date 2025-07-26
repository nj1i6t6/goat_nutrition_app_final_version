// --- START OF FILE frontend/src/data/options.js ---

// 這個檔案集中管理整個應用程式中可重用的下拉選單選項。

export const sexOptions = [
    { value: "", text: "請選擇..." },
    { value: "母", text: "母 (Female)" },
    { value: "公", text: "公 (Male)" },
    { value: "閹", text: "閹 (Wether)" }
];

export const breedCategoryOptions = [
    { value: "", text: "請選擇..." }, 
    { value: "Dairy", text: "乳用 (Dairy)" }, 
    { value: "Meat", text: "肉用 (Meat)" },
    { value: "Fiber", text: "毛用 (Fiber)" },
    { value: "DualPurpose", text: "兼用 (DualPurpose)" },
    { value: "Miniature", text: "小型/寵物 (Miniature)" }, 
    { value: "Other", text: "其他" }
];

export const statusOptions = [
    { value: "", text: "請選擇..." }, 
    { value: "maintenance", text: "維持期" },
    { value: "growing_young", text: "生長前期" },
    { value: "growing_finishing", text: "生長育肥期" },
    { value: "gestating_early", text: "懷孕早期" },
    { value: "gestating_late", text: "懷孕晚期" },
    { value: "lactating_early", text: "泌乳早期" },
    { value: "lactating_peak", text: "泌乳高峰期" },
    { value: "lactating_mid", text: "泌乳中期" },
    { value: "lactating_late", text: "泌乳晚期" },
    { value: "dry_period", text: "乾乳期" },
    { value: "breeding_male_active", text: "配種期公羊" },
    { value: "breeding_male_non_active", text: "非配種期公羊" },
    { value: "fiber_producing", text: "產毛期" },
    { value: "other_status", text: "其他 (請描述)" }
];

export const activityLevelOptions = [
    { value: "", text: "未指定" },
    { value: "confined", text: "舍飼/限制" },
    { value: "grazing_flat_pasture", text: "平地放牧" },
    { value: "grazing_hilly_pasture", text: "山地放牧" }
];

export const historyTypeMap = new Map([
    ["Body_Weight_kg", "體重 (公斤)"],
    ["milk_yield_kg_day", "日產奶量 (公斤/天)"],
    ["milk_fat_percentage", "乳脂率 (%)"],
]);

// --- END OF FILE frontend/src/data/options.js ---