# --- START OF FILE backend/run.py ---

import os
from app import create_app, db
from app.models import User, Sheep, SheepEvent
from dotenv import load_dotenv

# 載入 .env 檔案中的環境變數
# 這會尋找與 run.py 同層的 .env 檔案
load_dotenv()

# 透過應用程式工廠建立 app 實例
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """為 'flask shell' 命令提供預設的導入上下文，方便調試。"""
    return {'db': db, 'User': User, 'Sheep': Sheep, 'SheepEvent': SheepEvent}

if __name__ == '__main__':
    # 從環境變數獲取主機和端口，並提供預設值
    host = os.environ.get('FLASK_RUN_HOST', '0.0.0.0') 
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    
    # 根據 FLASK_DEBUG 環境變數決定是否啟用 debug 模式
    # 'False'.lower() in ['true', '1', 't'] -> False
    # 'True'.lower() in ['true', '1', 't'] -> True
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']

    print("===================================================")
    print(f" * 啟動 Goat Nutrition App (Refactored Backend)")
    print(f" * 正在 http://{host}:{port} 上運行")
    print(f" * Debug 模式: {'開啟' if debug else '關閉'}")
    print("===================================================")
    
    # 執行 Flask 應用
    # 在 debug 模式下，伺服器會在程式碼變更後自動重載
    app.run(host=host, port=port, debug=debug)

# --- END OF FILE backend/run.py ---