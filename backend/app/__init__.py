# --- START OF FILE backend/app/__init__.py ---

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

# 初始化擴展，但在工廠函數外部，這樣其他模組可以導入它們
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """
    應用程式工廠函數。
    這種模式允許我們為不同的環境（如測試、生產）創建不同的應用實例。
    """
    # 載入 .env 檔案中的環境變數
    # 確保在 create_app 內部也載入，以便在任何情境下都能讀取到
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    
    # 建立 Flask 應用實例
    # template_folder 指向 app 的父目錄下的 templates
    app = Flask(__name__, template_folder='../templates', static_folder=None)

    # --- 配置 ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    
    # 從 .env 檔案讀取資料庫的詳細資訊來組合 PostgreSQL 的連接字串
    db_user = os.environ.get('DB_USERNAME')
    db_pass = os.environ.get('DB_PASSWORD')
    db_host = os.environ.get('DB_HOST')
    db_port = os.environ.get('DB_PORT')
    db_name = os.environ.get('DB_NAME')
    db_uri = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- 初始化擴展 ---
    db.init_app(app)
    login_manager.init_app(app)

    # --- 設置 Flask-Login ---
    # 指定登入頁面的端點 (route)
    login_manager.login_view = 'auth.login'
    # 當使用者嘗試訪問需要登入的頁面時顯示的訊息
    login_manager.login_message = '請登入以訪問此頁面。'
    login_manager.login_message_category = 'info'

    # 使用應用程式上下文
    with app.app_context():
        # --- 註冊藍圖 (Blueprints) ---
        # 藍圖幫助我們將應用程式組織成更小的、可重用的部分
        from .routes import main_routes, auth_routes, api_routes
        app.register_blueprint(main_routes.bp)
        app.register_blueprint(auth_routes.bp)
        app.register_blueprint(api_routes.bp)

        # --- 建立資料庫表格 ---
        # 這將根據 models.py 中定義的模型在 PostgreSQL 中建立所有尚不存在的表格
        # 在生產環境中，通常會使用資料庫遷移工具如 Alembic 來管理 schema 變更
        db.create_all()

        return app

# --- END OF FILE backend/app/__init__.py ---