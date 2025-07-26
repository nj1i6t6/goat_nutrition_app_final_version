# --- START OF FILE backend/app/routes/main_routes.py ---

from flask import Blueprint, render_template, send_from_directory
from flask_login import login_required
import os

# 建立一個名為 'main' 的藍圖
bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    """
    渲染主應用程式頁面 (index.html)。
    這是前端 Vue 應用程式的進入點。
    """
    return render_template('index.html')

@bp.route('/download_template')
@login_required
def download_template():
    """
    提供標準 Excel 範本檔案的下載。
    """
    # templates 目錄現在位於 app 的父目錄
    template_dir = os.path.join(bp.root_path, '..', 'templates')
    return send_from_directory(template_dir, 'goat_import_template.xlsx', as_attachment=True)

# --- END OF FILE backend/app/routes/main_routes.py ---