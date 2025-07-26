# --- START OF FILE backend/app/services/ai_service.py ---

import requests
import json
from datetime import datetime
from ..models import ChatHistory, SheepHistoricalData
from . import sheep_service

def call_gemini_api(prompt_text_or_messages, api_key, generation_config_override=None):
    """
    通用的 Gemini API 調用函數。

    Args:
        prompt_text_or_messages (str or list): 可以是單一的字串提示，或是多輪對話的訊息列表。
        api_key (str): 使用者的 Gemini API 金鑰。
        generation_config_override (dict, optional): 用於覆蓋預設生成設定的字典。

    Returns:
        dict: 包含 'text'、'error' 或其他 API 回應資訊的字典。
    """
    GEMINI_MODEL_NAME = "gemini-2.5-flash"
    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL_NAME}:generateContent?key={api_key}"
    
    generation_config = {
        "temperature": 0.4, 
        "topK": 1, 
        "topP": 0.95, 
        "maxOutputTokens": 8192,
    }
    if generation_config_override: 
        generation_config.update(generation_config_override)

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    
    # 根據輸入類型組合 payload
    payload_contents = []
    if isinstance(prompt_text_or_messages, str):
        payload_contents.append({"role": "user", "parts": [{"text": prompt_text_or_messages}]})
    elif isinstance(prompt_text_or_messages, list):
        payload_contents = prompt_text_or_messages

    payload = {
        "contents": payload_contents,
        "generationConfig": generation_config,
        "safetySettings": safety_settings
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload), timeout=180)
        response.raise_for_status()
        result_json = response.json()

        if result_json.get("candidates"):
            candidate = result_json["candidates"][0]
            text_content = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
            return {"text": text_content}
        
        elif result_json.get("promptFeedback"):
            block_reason = result_json["promptFeedback"].get("blockReason", "未知原因")
            return {"error": f"提示詞被 Gemini 系統拒絕。原因：{block_reason}。"}
        else:
            return {"error": "API 回應格式不符合預期。", "raw_response": result_json}

    except requests.exceptions.HTTPError as e:
        error_message = f"API 請求失敗 (HTTP 狀態碼: {e.response.status_code})"
        try:
            error_detail = e.response.json()
            api_error_msg = error_detail.get("error", {}).get("message", "請檢查您的 API 金鑰是否有效或額度是否足夠。")
            error_message += f": {api_error_msg}"
        except (ValueError, json.JSONDecodeError):
            error_message += f": {e.response.text}"
        return {"error": error_message}
    except requests.exceptions.RequestException as e:
        return {"error": f"網路或請求錯誤: {e}"}


def get_daily_tip(api_key):
    """
    獲取每日飼養小提示。
    
    Returns:
        dict: 包含 'tip_html' 或 'error' 的字典。
    """
    current_month = datetime.now().month
    if current_month in [3, 4, 5]: season = "春季"
    elif current_month in [6, 7, 8]: season = "夏季"
    elif current_month in [9, 10, 11]: season = "秋季"
    else: season = "冬季"
    
    prompt = (
        f"作為『領頭羊博士』，請給我一條關於台灣當前「{season}」的實用山羊飼養小提示。"
        "內容需簡短且易懂，請使用 Markdown 格式，並將重點字詞用 `**` 包裹起來。"
    )
    
    return call_gemini_api(prompt, api_key, generation_config_override={"temperature": 0.7})


def get_feeding_recommendation(api_key, user_id, form_data):
    """
    根據使用者提供的羊隻數據，產生飼養建議。
    """
    ear_num = form_data.get('EarNum')
    context_str = _build_sheep_context_string(user_id, ear_num)
    prompt = _build_recommendation_prompt(form_data, context_str)
    
    return call_gemini_api(prompt, api_key)


def get_chat_response(api_key, user_id, session_id, user_message, ear_num_context):
    """
    處理與 AI 助手的多輪對話。
    """
    history = ChatHistory.query.filter_by(
        user_id=user_id, 
        session_id=session_id
    ).order_by(ChatHistory.timestamp.asc()).limit(20).all()
    
    chat_messages = _build_chat_history_for_api(history)
    
    sheep_context_str = _build_sheep_context_string(user_id, ear_num_context)
    
    current_user_message_with_context = user_message + sheep_context_str
    chat_messages.append({"role": "user", "parts": [{"text": current_user_message_with_context}]})
    
    return call_gemini_api(chat_messages, api_key, generation_config_override={"temperature": 0.7})


# --- Private Helper Functions ---

def _build_sheep_context_string(user_id, ear_num):
    """
    (私有) 根據耳號組合羊隻背景資料字串，用於豐富提示詞。
    """
    if not ear_num:
        return ""
    
    sheep_info = sheep_service.get_sheep_details_by_ear_num(user_id, ear_num)
    if not sheep_info:
        return ""

    context_parts = [f"\n\n--- 關於耳號 {sheep_info['EarNum']} 的額外背景資料 ---"]
    if sheep_info.get('agent_notes'):
        context_parts.append(f"我的觀察筆記: {sheep_info['agent_notes']}")

    history_records = SheepHistoricalData.query.filter_by(
        sheep_id=sheep_info['id'], user_id=user_id
    ).order_by(SheepHistoricalData.record_date.desc()).limit(10).all()

    if history_records:
        history_by_type = {}
        for rec in reversed(history_records):
            rec_type = rec.record_type
            if rec_type not in history_by_type:
                history_by_type[rec_type] = []
            history_by_type[rec_type].append(f"{rec.record_date}({rec.value})")
        
        context_parts.append("歷史數據趨勢:")
        for rec_type, values_str in history_by_type.items():
            context_parts.append(f"- {rec_type}: {', '.join(values_str)}")

    if sheep_info.get('events'):
        context_parts.append("近期事件:")
        for event in sheep_info['events'][:5]: # 最多顯示 5 筆
            desc = event.get('description') or '無描述'
            context_parts.append(f"- {event['event_date']} {event['event_type']}: {desc}")
            
    return "\n".join(context_parts)


def _build_recommendation_prompt(form_data, context_str):
    """
    (私有) 組合飼養建議的完整提示詞。
    """
    status_map = {
        "maintenance":"維持期", "growing_young":"生長前期", "growing_finishing":"生長育肥期",
        "gestating_early":"懷孕早期", "gestating_late":"懷孕晚期", "lactating_early":"泌乳早期",
        "lactating_peak":"泌乳高峰期", "lactating_mid":"泌乳中期", "lactating_late":"泌乳晚期",
        "dry_period":"乾乳期", "breeding_male_active":"配種期公羊", "breeding_male_non_active":"非配種期公羊",
        "fiber_producing":"產毛期", "other_status":"其他"
    }
    status_display = status_map.get(form_data.get('status'), form_data.get('status'))
    if form_data.get('status') == 'other_status' and form_data.get('status_description'):
        status_display = form_data.get('status_description')

    prompt_parts = [
        f"你是一位名叫『領頭羊博士』的AI羊隻飼養代理人，你非常了解台灣的氣候和常見飼養方式，並且嚴格遵循美國國家科學研究委員會 NRC (2007) 《Nutrient Requirements of Small Ruminants》的指南。",
        f"你正在為耳號為 **{form_data.get('EarNum', '一隻未指定耳號')}** 的羊隻提供飼養營養建議。",
        "請根據以下提供的羊隻數據和背景資料，提供一份每日飼料營養需求的詳細建議，包括DMI, ME, CP, Ca, P, 鈣磷比，以及其他適用礦物質和維生素。並針對特定生理狀態給予台灣本土化操作建議。請用 Markdown 格式清晰呈現。\n",
        "--- 羊隻當前數據 ---"
    ]
    
    # 動態加入有值的欄位
    field_map = {
        'EarNum': '耳號', 'Breed': '品種', 'Body_Weight_kg': '體重 (公斤)', 
        'Age_Months': '月齡', 'Sex': '性別'
    }
    for key, label in field_map.items():
        if form_data.get(key):
            prompt_parts.append(f"- {label}: {form_data[key]}")

    prompt_parts.append(f"- 生理狀態: {status_display}")
    
    if form_data.get('target_average_daily_gain_g') is not None:
        prompt_parts.append(f"- 目標日增重: {form_data['target_average_daily_gain_g']} g/天")
    if form_data.get('milk_yield_kg_day') is not None:
        prompt_parts.append(f"- 日產奶量: {form_data['milk_yield_kg_day']} kg/天")
    if form_data.get('milk_fat_percentage') is not None:
        prompt_parts.append(f"- 乳脂率: {form_data['milk_fat_percentage']}%")
    if form_data.get('number_of_fetuses') is not None:
        prompt_parts.append(f"- 懷胎數: {form_data['number_of_fetuses']}")

    full_prompt = "\n".join(prompt_parts) + context_str
    if form_data.get('other_remarks'):
        full_prompt += f"\n\n--- 使用者提供的其他備註 ---\n{form_data.get('other_remarks')}"
    
    full_prompt += "\n\n請提供您的專業建議。"
    return full_prompt


def _build_chat_history_for_api(history_from_db):
    """
    (私有) 將資料庫中的聊天記錄轉換為 API 需要的格式。
    """
    system_prompt = "你是一位名叫『領頭羊博士』的AI羊隻飼養代理人，你非常了解台灣的氣候和常見飼養方式。請友善且專業地回答使用者的問題。"
    
    messages = [
        {"role": "user", "parts": [{"text": system_prompt}]},
        {"role": "model", "parts": [{"text": "是的，領頭羊博士在此為您服務。請問有什麼問題嗎？"}]}
    ]
    for entry in history_from_db:
        messages.append({"role": entry.role, "parts": [{"text": entry.content}]})
        
    return messages

# --- END OF FILE backend/app/services/ai_service.py ---