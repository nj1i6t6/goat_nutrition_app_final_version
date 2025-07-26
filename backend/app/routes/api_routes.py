# --- START OF FILE backend/app/routes/api_routes.py ---

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
from ..services import sheep_service, user_service, data_service, ai_service
import markdown
from datetime import datetime # <--- 修正處：補上這個 import

# 建立一個名為 'api' 的藍圖，並設定 URL 前綴為 /api
bp = Blueprint('api', __name__, url_prefix='/api')

# --- Helper for error handling ---
def handle_service_call(service_func, *args, **kwargs):
    """一個輔助函數，用於調用服務層函數並處理常見的例外情況。"""
    try:
        result = service_func(*args, **kwargs)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400 # Bad Request
    except Exception as e:
        # 在生產環境中應記錄詳細錯誤
        current_app.logger.error(f"API Error in {service_func.__name__}: {e}")
        return jsonify({"error": "伺服器內部錯誤"}), 500

# --- Sheep (羊隻) API ---
@bp.route('/sheep', methods=['GET'])
@login_required
def get_all_sheep():
    return handle_service_call(sheep_service.get_all_sheep_by_user, current_user.id)

@bp.route('/sheep', methods=['POST'])
@login_required
def add_sheep():
    data = request.get_json()
    try:
        new_sheep_dict = sheep_service.add_sheep(current_user.id, data)
        return jsonify({"success": True, "message": "羊隻資料新增成功", "sheep": new_sheep_dict}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409 # Conflict
    except Exception as e:
        current_app.logger.error(f"新增羊隻失敗: {e}")
        return jsonify({"error": "新增羊隻失敗"}), 500

@bp.route('/sheep/<ear_num>', methods=['GET'])
@login_required
def get_sheep_details(ear_num):
    details = sheep_service.get_sheep_details_by_ear_num(current_user.id, ear_num)
    if details:
        return jsonify(details)
    return jsonify({"error": "找不到該耳號的羊隻或您沒有權限"}), 404

@bp.route('/sheep/<ear_num>', methods=['PUT'])
@login_required
def update_sheep(ear_num):
    data = request.get_json()
    try:
        updated_sheep = sheep_service.update_sheep_data(current_user.id, ear_num, data)
        return jsonify({"success": True, "message": "羊隻資料更新成功，並已自動記錄歷史數據。", "sheep": updated_sheep})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"更新羊隻 {ear_num} 失敗: {e}")
        return jsonify({"error": "更新羊隻失敗"}), 500

@bp.route('/sheep/<ear_num>', methods=['DELETE'])
@login_required
def delete_sheep(ear_num):
    try:
        sheep_service.delete_sheep_by_ear_num(current_user.id, ear_num)
        return jsonify({"success": True, "message": "羊隻資料刪除成功"})
    except Exception as e:
        current_app.logger.error(f"刪除羊隻 {ear_num} 失敗: {e}")
        return jsonify({"error": "刪除羊隻失敗"}), 500

# --- SheepEvent (事件) API ---
@bp.route('/sheep/<ear_num>/events', methods=['GET'])
@login_required
def get_sheep_events(ear_num):
    return handle_service_call(sheep_service.get_events_for_sheep, current_user.id, ear_num)

@bp.route('/sheep/<ear_num>/events', methods=['POST'])
@login_required
def add_sheep_event(ear_num):
    data = request.get_json()
    try:
        new_event = sheep_service.add_sheep_event(current_user.id, ear_num, data)
        return jsonify({"success": True, "message": "羊隻事件新增成功", "event": new_event}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"新增羊隻事件失敗: {e}")
        return jsonify({"error": "新增羊隻事件失敗"}), 500

@bp.route('/events/<int:event_id>', methods=['PUT'])
@login_required
def update_event(event_id):
    data = request.get_json()
    return handle_service_call(sheep_service.update_sheep_event, current_user.id, event_id, data)

@bp.route('/events/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    try:
        sheep_service.delete_sheep_event(current_user.id, event_id)
        return jsonify({"success": True, "message": "事件刪除成功"})
    except Exception as e:
        current_app.logger.error(f"刪除事件 {event_id} 失敗: {e}")
        return jsonify({"error": "刪除事件失敗"}), 500

# --- Event Options API ---
@bp.route('/event_options', methods=['GET'])
@login_required
def get_event_options():
    return handle_service_call(user_service.get_all_event_options, current_user.id)

@bp.route('/event_types', methods=['POST'])
@login_required
def add_event_type():
    data = request.get_json()
    name = data.get('name')
    if not name: return jsonify({"error": "類型名稱為必填"}), 400
    return handle_service_call(user_service.add_event_type, current_user.id, name)

@bp.route('/event_types/<int:option_id>', methods=['DELETE'])
@login_required
def delete_event_type(option_id):
    return handle_service_call(user_service.delete_event_type, current_user.id, option_id)

@bp.route('/event_descriptions', methods=['POST'])
@login_required
def add_event_description():
    data = request.get_json()
    type_id = data.get('event_type_option_id')
    description = data.get('description')
    if not all([type_id, description]):
        return jsonify({"error": "缺少必要參數"}), 400
    return handle_service_call(user_service.add_event_description, current_user.id, type_id, description)

@bp.route('/event_descriptions/<int:option_id>', methods=['DELETE'])
@login_required
def delete_event_description(option_id):
    return handle_service_call(user_service.delete_event_description, current_user.id, option_id)

# --- Historical Data API ---
@bp.route('/sheep/<ear_num>/history', methods=['GET'])
@login_required
def get_sheep_history(ear_num):
    return handle_service_call(sheep_service.get_history_for_sheep, current_user.id, ear_num)

@bp.route('/history/<int:record_id>', methods=['DELETE'])
@login_required
def delete_sheep_history(record_id):
    try:
        sheep_service.delete_sheep_history(current_user.id, record_id)
        return jsonify({"success": True, "message": "歷史數據刪除成功"})
    except Exception as e:
        current_app.logger.error(f"刪除歷史數據 {record_id} 失敗: {e}")
        return jsonify({"error": "刪除歷史數據失敗"}), 500

# --- Data Management API ---
@bp.route('/data/export_excel', methods=['GET'])
@login_required
def export_excel():
    try:
        excel_binary = data_service.export_user_data_to_excel(current_user.id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"goat_data_export_{timestamp}.xlsx"
        return send_file(
            excel_binary,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        current_app.logger.error(f"匯出 Excel 失敗: {e}")
        return jsonify({"error": f"匯出 Excel 失敗: {str(e)}"}), 500

@bp.route('/data/analyze_excel', methods=['POST'])
@login_required
def analyze_excel():
    if 'file' not in request.files:
        return jsonify({"error": "沒有檔案被上傳"}), 400
    file = request.files['file']
    try:
        sheets_data = data_service.analyze_excel_file(file.stream)
        return jsonify({"success": True, "sheets": sheets_data})
    except Exception as e:
        current_app.logger.error(f"分析 Excel 檔案失敗: {e}")
        return jsonify({"error": f"分析 Excel 檔案失敗: {str(e)}"}), 500

@bp.route('/data/process_import', methods=['POST'])
@login_required
def process_import():
    if 'file' not in request.files:
        return jsonify({"error": "請求缺少檔案參數"}), 400
    
    file = request.files['file']
    is_default_mode = request.form.get('is_default_mode', 'false').lower() == 'true'
    mapping_config_str = request.form.get('mapping_config', '{}')

    try:
        report_details = data_service.import_data_from_excel(
            current_user.id, file.stream, mapping_config_str, is_default_mode
        )
        return jsonify({"success": True, "message": "數據導入已成功完成！", "details": report_details})
    except Exception as e:
        current_app.logger.error(f"導入 Excel 數據失敗: {e}")
        return jsonify({"error": f"導入數據過程中發生錯誤: {str(e)}"}), 500

# --- Dashboard API ---
@bp.route('/dashboard_data', methods=['GET'])
@login_required
def get_dashboard_data():
    return handle_service_call(sheep_service.get_dashboard_data, current_user.id)

# --- AI Agent API ---
@bp.route('/agent_tip', methods=['GET'])
@login_required
def get_agent_tip():
    api_key = request.headers.get('X-Api-Key')
    if not api_key: return jsonify({"error": "未提供API金鑰"}), 401
    
    result = ai_service.get_daily_tip(api_key)
    if "error" in result:
        return jsonify({"error": result['error']}), 500
    
    tip_html = markdown.markdown(result.get("text", "無法獲取提示。"), extensions=['nl2br'])
    return jsonify({"tip_html": tip_html})

@bp.route('/recommendation', methods=['POST'])
@login_required
def get_recommendation():
    data = request.get_json()
    api_key = data.pop('api_key', None)
    if not api_key: return jsonify({"error": "未提供 API 金鑰"}), 401
    
    result = ai_service.get_feeding_recommendation(api_key, current_user.id, data)
    if "error" in result:
        return jsonify({"error": result['error']}), 500
        
    recommendation_html = markdown.markdown(result.get("text", ""), extensions=['fenced_code', 'tables', 'nl2br'])
    return jsonify({"recommendation_html": recommendation_html})

@bp.route('/chat_with_agent', methods=['POST'])
@login_required
def chat_with_agent():
    data = request.get_json()
    api_key = data.get('api_key')
    user_message = data.get('message')
    session_id = data.get('session_id')
    ear_num_context = data.get('ear_num_context')

    if not all([api_key, user_message, session_id]):
        return jsonify({"error": "缺少必要參數"}), 400

    result = ai_service.get_chat_response(api_key, current_user.id, session_id, user_message, ear_num_context)
    if "error" in result:
        return jsonify(result), 500
    
    model_reply_text = result.get("text", "抱歉，我暫時無法回答。")

    try:
        sheep_service.save_chat_messages(current_user.id, session_id, ear_num_context, user_message, model_reply_text)
    except Exception as e:
        current_app.logger.error(f"儲存聊天記錄失敗: {e}")
        # 不阻斷對使用者的回覆
    
    reply_html = markdown.markdown(model_reply_text, extensions=['fenced_code', 'tables', 'nl2br'])
    return jsonify({"reply_html": reply_html})


# --- END OF FILE backend/app/routes/api_routes.py ---