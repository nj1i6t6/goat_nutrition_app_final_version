# --- START OF FILE backend/app/services/data_service.py ---

import pandas as pd
import json
from io import BytesIO
from datetime import datetime
from .. import db
from ..models import Sheep, SheepEvent, SheepHistoricalData, ChatHistory
from . import sheep_service

def export_user_data_to_excel(user_id):
    """
    將指定使用者的所有數據匯出成一個 Excel 檔案的二進位內容。

    Args:
        user_id (int): 使用者的 ID。

    Returns:
        BytesIO: 包含 Excel 檔案內容的 BytesIO 物件。
    """
    db_engine = db.get_engine()

    # 建立查詢
    sheep_query = Sheep.query.filter_by(user_id=user_id).order_by(Sheep.EarNum)
    events_query = SheepEvent.query.join(Sheep).filter(Sheep.user_id == user_id).order_by(Sheep.EarNum, SheepEvent.event_date.desc())
    history_query = SheepHistoricalData.query.join(Sheep).filter(Sheep.user_id == user_id).order_by(Sheep.EarNum, SheepHistoricalData.record_date)
    chat_query = ChatHistory.query.filter_by(user_id=user_id).order_by(ChatHistory.timestamp)

    # 讀取數據到 DataFrame
    df_sheep = pd.read_sql(sheep_query.statement, db_engine)
    df_events = pd.read_sql(events_query.statement, db_engine)
    df_history = pd.read_sql(history_query.statement, db_engine)
    df_chat = pd.read_sql(chat_query.statement, db_engine)

    # 建立 Excel 檔案
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if not df_sheep.empty:
            df_sheep.to_excel(writer, sheet_name='Sheep_Basic_Info', index=False)
        
        sheep_map = {s.id: s.EarNum for s in sheep_query.all()}
        
        if not df_events.empty:
            df_events['EarNum'] = df_events['sheep_id'].map(sheep_map)
            cols = ['EarNum'] + [col for col in df_events.columns if col not in ['EarNum', 'sheep_id', 'user_id']]
            df_events[cols].to_excel(writer, sheet_name='Sheep_Events_Log', index=False)

        if not df_history.empty:
            df_history['EarNum'] = df_history['sheep_id'].map(sheep_map)
            cols = ['EarNum'] + [col for col in df_history.columns if col not in ['EarNum', 'sheep_id', 'user_id']]
            df_history[cols].to_excel(writer, sheet_name='Sheep_Historical_Data', index=False)
        
        if not df_chat.empty:
            df_chat.to_excel(writer, sheet_name='Chat_History', index=False)
            
    output.seek(0)
    return output

def analyze_excel_file(file_stream):
    """
    分析上傳的 Excel 檔案，返回其結構資訊。
    """
    try:
        xls = pd.ExcelFile(file_stream)
        sheets_data = {}
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)
            df = df.where(pd.notna(df), None) # 將 NaN 轉換為 None
            preview_data = df.head(3).to_dict(orient='records')
            sheets_data[sheet_name] = {
                "columns": list(df.columns),
                "rows": len(df),
                "preview": preview_data
            }
        return sheets_data
    except Exception as e:
        # 可以記錄更詳細的日誌
        raise ValueError(f"分析 Excel 檔案失敗: {e}")

def import_data_from_excel(user_id, file_stream, config_str, is_default_mode):
    """
    根據提供的設定，從 Excel 檔案導入數據。
    """
    if is_default_mode:
        config = _get_default_import_config()
    else:
        try:
            config = json.loads(config_str)
        except json.JSONDecodeError:
            raise ValueError("手動模式請求的映射設定格式錯誤")
    
    try:
        xls = pd.ExcelFile(file_stream)
        report_details = []
        
        # 預加載資料以提高效能
        sheep_id_cache = {s.EarNum: s.id for s in Sheep.query.filter_by(user_id=user_id).all()}
        
        # 1. 處理對照表
        breed_map, sex_map = _process_mapping_sheets(xls, config)
        
        # 2. 處理基礎資料
        report_basic, sheep_id_cache = _process_basic_info_sheet(xls, config, user_id, breed_map, sex_map, sheep_id_cache)
        if report_basic:
            report_details.append(report_basic)

        # 3. 處理事件和歷史數據表
        event_reports = _process_event_and_history_sheets(xls, config, user_id, sheep_id_cache)
        report_details.extend(event_reports)
        
        db.session.commit()
        return report_details
        
    except Exception as e:
        db.session.rollback()
        raise Exception(f"導入數據過程中發生錯誤: {e}")

# --- Private Helper Functions ---

def _get_default_import_config():
    """返回預設導入模式的設定檔。"""
    return {
        "sheets": {
            "0009-0013A1_Basic": {"purpose": "basic_info", "columns": { "EarNum": "EarNum", "Breed": "Breed", "Sex": "Sex", "BirthDate": "BirthDate", "Sire": "Sire", "Dam": "Dam", "BirWei": "BirWei", "SireBre": "SireBre", "DamBre": "DamBre", "MoveCau": "MoveCau", "MoveDate": "MoveDate", "Class": "Class", "LittleSize": "LittleSize", "Lactation": "Lactation", "ManaClas": "ManaClas", "FarmNum": "FarmNum", "RUni": "RUni" }},
            "0009-0013A4_Kidding": {"purpose": "kidding_record", "columns": { "EarNum": "EarNum", "YeanDate": "YeanDate", "KidNum": "KidNum", "KidSex": "KidSex" }},
            "0009-0013A2_PubMat": {"purpose": "mating_record", "columns": { "EarNum": "EarNum", "Mat_date": "Mat_date", "Mat_grouM_Sire": "Mat_grouM_Sire" }},
            "0009-0013A3_Yean": {"purpose": "yean_record", "columns": { "EarNum": "EarNum", "YeanDate": "YeanDate", "DryOffDate": "DryOffDate", "Lactation": "Lactation" }},
            "0009-0013A9_Milk": {"purpose": "milk_yield_record", "columns": { "EarNum": "EarNum", "MeaDate": "MeaDate", "Milk": "Milk" }},
            "0009-0013A11_MilkAnalysis": {"purpose": "milk_analysis_record", "columns": { "EarNum": "EarNum", "MeaDate": "MeaDate", "AMFat": "AMFat" }},
            "S2_Breed": {"purpose": "breed_mapping", "columns": { "Code": "Symbol", "Name": "Breed" }},
            "S7_Sex": {"purpose": "sex_mapping", "columns": { "Code": "Num", "Name": "Sex" }}
        }
    }

def _format_date(d):
    """格式化日期，處理各種可能的輸入格式。"""
    if not d or pd.isna(d): return None
    try:
        # 先轉為字串並取日期部分，避免時間戳問題
        d_str = str(d).split(' ')[0]
        # 使用 pandas 的 to_datetime 進行穩健的轉換
        dt = pd.to_datetime(d_str, errors='coerce')
        if pd.isna(dt) or dt.year < 1901: return None
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return None

def _process_mapping_sheets(xls, config):
    """從 Excel 中讀取品種和性別的對照表。"""
    breed_map, sex_map = {}, {}
    for sheet_name, sheet_config in config.get('sheets', {}).items():
        if sheet_name not in xls.sheet_names: continue
        purpose = sheet_config.get('purpose')
        cols = sheet_config.get('columns', {})
        df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str).where(pd.notna, None)
        
        if purpose == 'breed_mapping' and all(k in cols for k in ['Code', 'Name']):
            for _, row in df.iterrows():
                if row.get(cols['Code']): breed_map[str(row[cols['Code']])] = row[cols['Name']]
        elif purpose == 'sex_mapping' and all(k in cols for k in ['Code', 'Name']):
            for _, row in df.iterrows():
                if row.get(cols['Code']): sex_map[str(row[cols['Code']])] = row[cols['Name']]
    return breed_map, sex_map

def _process_basic_info_sheet(xls, config, user_id, breed_map, sex_map, sheep_id_cache):
    """處理基礎資料工作表，創建或更新羊隻記錄。"""
    created, updated = 0, 0
    sheet_name_processed = None

    for sheet_name, sheet_config in config.get('sheets', {}).items():
        if sheet_config.get('purpose') == 'basic_info':
            if sheet_name not in xls.sheet_names: continue
            cols = sheet_config.get('columns', {})
            if 'EarNum' not in cols: continue
            
            sheet_name_processed = sheet_name
            df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str).where(pd.notna, None)
            
            for _, row in df.iterrows():
                ear_num = row.get(cols['EarNum'])
                if not ear_num: continue

                sheep = Sheep.query.filter_by(user_id=user_id, EarNum=ear_num).first()
                if not sheep:
                    sheep = Sheep(user_id=user_id, EarNum=ear_num)
                    db.session.add(sheep)
                    created += 1
                else:
                    updated += 1
                
                for db_field, xls_col in cols.items():
                    if hasattr(sheep, db_field) and xls_col in row and row[xls_col] is not None:
                        value = row[xls_col]
                        if db_field == 'Breed': value = breed_map.get(str(value), value)
                        elif db_field == 'Sex': value = sex_map.get(str(value), value)
                        elif 'Date' in db_field: value = _format_date(value)
                        
                        if value is not None:
                            setattr(sheep, db_field, value)
            
            db.session.flush() # 將變更寫入事務，以便更新 sheep_id_cache
            new_sheep_id_cache = {s.EarNum: s.id for s in Sheep.query.filter_by(user_id=user_id).all()}
            
            report = {"sheet": sheet_name, "message": f"處理完成。新增 {created} 筆，更新 {updated} 筆基礎資料。"}
            return report, new_sheep_id_cache

    return None, sheep_id_cache # 如果沒有基礎資料表

def _process_event_and_history_sheets(xls, config, user_id, sheep_id_cache):
    """處理所有非基礎資料的工作表，轉換為事件或歷史數據。"""
    reports = []
    for sheet_name, sheet_config in config.get('sheets', {}).items():
        purpose = sheet_config.get('purpose')
        if purpose in ['ignore', 'basic_info', 'breed_mapping', 'sex_mapping'] or sheet_name not in xls.sheet_names:
            continue
            
        cols = sheet_config.get('columns', {})
        df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str).where(pd.notna, None)
        count = 0
        
        for _, row in df.iterrows():
            ear_num = row.get(cols.get('EarNum'))
            sheep_id = sheep_id_cache.get(ear_num)
            if not sheep_id: continue
            
            # 根據 purpose 創建事件或歷史數據
            try:
                if purpose == 'kidding_record':
                    date = _format_date(row.get(cols.get('YeanDate')))
                    if date:
                        desc = f"產下仔羊: {row.get(cols.get('KidNum'))}" if cols.get('KidNum') else None
                        db.session.add(SheepEvent(user_id=user_id, sheep_id=sheep_id, event_date=date, event_type='產仔', description=desc))
                        count += 1
                elif purpose == 'mating_record':
                    date = _format_date(row.get(cols.get('Mat_date')))
                    if date:
                        desc = f"配種公羊: {row.get(cols.get('Mat_grouM_Sire'))}" if cols.get('Mat_grouM_Sire') else None
                        db.session.add(SheepEvent(user_id=user_id, sheep_id=sheep_id, event_date=date, event_type='配種', description=desc))
                        count += 1
                elif purpose == 'yean_record':
                    lactation = row.get(cols.get('Lactation'))
                    if yean_date := _format_date(row.get(cols.get('YeanDate'))):
                        db.session.add(SheepEvent(user_id=user_id, sheep_id=sheep_id, event_date=yean_date, event_type='泌乳開始', description=f"第 {lactation} 胎次"))
                        count += 1
                    if dry_off_date := _format_date(row.get(cols.get('DryOffDate'))):
                        db.session.add(SheepEvent(user_id=user_id, sheep_id=sheep_id, event_date=dry_off_date, event_type='乾乳', description=f"第 {lactation} 胎次結束"))
                        count += 1
                elif purpose in ['weight_record', 'milk_yield_record', 'milk_analysis_record']:
                    type_map = {
                        'weight_record': ('Body_Weight_kg', 'Weight'),
                        'milk_yield_record': ('milk_yield_kg_day', 'Milk'),
                        'milk_analysis_record': ('milk_fat_percentage', 'AMFat')
                    }
                    hist_type, val_col = type_map[purpose]
                    date = _format_date(row.get(cols.get('MeaDate')))
                    value = row.get(cols.get(val_col))
                    if date and value is not None:
                        db.session.add(SheepHistoricalData(user_id=user_id, sheep_id=sheep_id, record_date=date, record_type=hist_type, value=float(value)))
                        count += 1
            except (ValueError, TypeError):
                # 忽略無法轉換的行
                continue

        if count > 0:
            reports.append({"sheet": sheet_name, "message": f"成功導入 {count} 筆記錄。"})
            
    return reports

# --- END OF FILE backend/app/services/data_service.py ---