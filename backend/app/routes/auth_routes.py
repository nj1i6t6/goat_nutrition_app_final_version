# --- START OF FILE backend/app/routes/auth_routes.py ---

from flask import Blueprint, render_template, request, jsonify, url_for, redirect, flash
from flask_login import login_user, logout_user, current_user, login_required
from ..services import user_service

# 【修正】為所有認證路由統一加上 /api/auth 前綴
bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# 現在的完整路徑是: POST /api/auth/login
@bp.route('/login', methods=['POST'])
def login_api():
    """處理使用者登入的 API 請求。"""
    if current_user.is_authenticated:
        return jsonify({'success': False, 'message': '您已登入'}), 400

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = user_service.authenticate_user(username, password)
    
    if user:
        login_user(user, remember=True)
        return jsonify({'success': True, 'user': {'username': user.username}})
    else:
        return jsonify({'success': False, 'message': '無效的使用者名稱或密碼'}), 401

# 現在的完整路徑是: POST /api/auth/register
@bp.route('/register', methods=['POST'])
def register_api():
    """處理使用者註冊的 API 請求。"""
    if current_user.is_authenticated:
        return jsonify({'success': False, 'message': '您已登入'}), 400

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    try:
        new_user = user_service.create_user_with_defaults(username, password)
        login_user(new_user, remember=True)
        return jsonify({'success': True, 'user': {'username': new_user.username}}), 201
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 409
    except Exception as e:
        return jsonify({'success': False, 'message': f'註冊過程中發生未知錯誤'}), 500

# 現在的完整路徑是: POST /api/auth/logout
@bp.route('/logout', methods=['POST'])
@login_required
def logout_api():
    """處理使用者登出的 API 請求。"""
    logout_user()
    return jsonify({'success': True, 'message': '您已成功登出'})

# 現在的完整路徑是: GET /api/auth/status
@bp.route('/status', methods=['GET'])
def auth_status():
    """檢查當前使用者的登入狀態的 API 請求。"""
    if current_user.is_authenticated:
        return jsonify({'logged_in': True, 'username': current_user.username})
    else:
        return jsonify({'logged_in': False})

# --- END OF FILE backend/app/routes/auth_routes.py ---