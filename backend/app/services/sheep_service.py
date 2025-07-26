# --- START OF FILE backend/app/services/sheep_service.py ---

from .. import db
from ..models import User, Sheep, SheepEvent, SheepHistoricalData, ChatHistory
from datetime import datetime, date, timedelta

# --- Sheep (羊隻) CRUD 服務 ---

def add_sheep(user_id, data):
    ear_num = data.get('EarNum')
    if not ear_num:
        raise ValueError("'EarNum' 為必填欄位")
    if Sheep.query.filter_by(user_id=user_id, EarNum=ear_num).first():
        raise ValueError(f"耳號 {ear_num} 已存在")
    
    # 清理所有不应由用户在创建时指定的键
    allowed_fields = {field.name for field in Sheep.__table__.columns if field.name not in ['id', 'user_id']}
    clean_data = {key: value for key, value in data.items() if key in allowed_fields}

    new_sheep = Sheep(user_id=user_id, **clean_data)
    db.session.add(new_sheep)
    db.session.commit()
    return new_sheep.to_dict()

def get_all_sheep_by_user(user_id):
    sheep_list = Sheep.query.filter_by(user_id=user_id).order_by(Sheep.EarNum).all()
    return [s.to_dict() for s in sheep_list]

def get_sheep_details_by_ear_num(user_id, ear_num):
    sheep = Sheep.query.filter_by(user_id=user_id, EarNum=ear_num).first()
    if not sheep: return None
    sheep_data = sheep.to_dict()
    events = SheepEvent.query.filter_by(sheep_id=sheep.id).order_by(SheepEvent.event_date.desc(), SheepEvent.id.desc()).limit(10).all()
    sheep_data['events'] = [e.to_dict() for e in events]
    return sheep_data

def update_sheep_data(user_id, ear_num, data):
    sheep_to_update = db.session.query(Sheep).filter_by(user_id=user_id, EarNum=ear_num).first()
    if not sheep_to_update: raise ValueError(f"找不到耳號為 {ear_num} 的羊隻")

    record_date = data.pop('record_date', date.today().strftime('%Y-%m-%d'))
    if not record_date: record_date = date.today().strftime('%Y-%m-%d')
    
    historical_fields = ['Body_Weight_kg', 'milk_yield_kg_day', 'milk_fat_percentage']
    
    allowed_fields = {field.name for field in Sheep.__table__.columns if field.name not in ['id', 'user_id', 'EarNum']}

    for key, value in data.items():
        if key in allowed_fields:
            old_value = getattr(sheep_to_update, key)
            new_value = value if value != '' else None
            
            if key in historical_fields and new_value is not None:
                try:
                    if old_value is None or float(old_value) != float(new_value):
                        history_record = SheepHistoricalData(
                            sheep_id=sheep_to_update.id, user_id=user_id, record_date=record_date,
                            record_type=key, value=float(new_value), notes=f"從 {old_value} 更新為 {new_value}"
                        )
                        db.session.add(history_record)
                except (ValueError, TypeError): pass
            
            setattr(sheep_to_update, key, new_value)
    
    sheep_to_update.last_updated = datetime.utcnow()
    db.session.commit()
    return sheep_to_update.to_dict()

def delete_sheep_by_ear_num(user_id, ear_num):
    sheep = Sheep.query.filter_by(user_id=user_id, EarNum=ear_num).first_or_404()
    db.session.delete(sheep)
    db.session.commit()

# --- SheepEvent (事件) CRUD 服務 ---

def add_sheep_event(user_id, ear_num, data):
    """【重大修正V4】只提取需要的欄位來創建物件"""
    sheep = Sheep.query.filter_by(user_id=user_id, EarNum=ear_num).first_or_404()
    
    event_date = data.get('event_date')
    event_type = data.get('event_type')

    if not event_date or not event_type:
        raise ValueError("事件日期和類型為必填")
        
    new_event = SheepEvent(
        user_id=user_id,
        sheep_id=sheep.id,
        event_date=event_date,
        event_type=event_type,
        description=data.get('description'),
        notes=data.get('notes')
    )
    db.session.add(new_event)
    db.session.commit()
    return new_event.to_dict()

def get_events_for_sheep(user_id, ear_num):
    sheep = Sheep.query.filter_by(user_id=user_id, EarNum=ear_num).first_or_404()
    events = SheepEvent.query.filter_by(sheep_id=sheep.id).order_by(SheepEvent.event_date.desc(), SheepEvent.id.desc()).all()
    return [e.to_dict() for e in events]

def update_sheep_event(user_id, event_id, data):
    """【重大修正V4】只更新允許的欄位"""
    event = SheepEvent.query.filter_by(id=event_id, user_id=user_id).first_or_404()
    
    event_date = data.get('event_date')
    event_type = data.get('event_type')

    if not event_date or not event_type:
        raise ValueError("事件日期和類型為必填")
        
    event.event_date = event_date
    event.event_type = event_type
    event.description = data.get('description')
    event.notes = data.get('notes')
    db.session.commit()
    return event.to_dict()

def delete_sheep_event(user_id, event_id):
    event = SheepEvent.query.filter_by(id=event_id, user_id=user_id).first_or_404()
    db.session.delete(event)
    db.session.commit()

# --- SheepHistoricalData (歷史數據) 服務 ---
def get_history_for_sheep(user_id, ear_num):
    sheep = Sheep.query.filter_by(user_id=user_id, EarNum=ear_num).first_or_404()
    history = SheepHistoricalData.query.filter_by(sheep_id=sheep.id).order_by(SheepHistoricalData.record_date.asc(), SheepHistoricalData.id.asc()).all()
    return [h.to_dict() for h in history]

def delete_sheep_history(user_id, record_id):
    record = SheepHistoricalData.query.filter_by(id=record_id, user_id=user_id).first_or_404()
    db.session.delete(record)
    db.session.commit()

# --- ChatHistory (聊天記錄) 服務 ---
def save_chat_messages(user_id, session_id, ear_num_context, user_message, model_reply):
    user_entry = ChatHistory(user_id=user_id, session_id=session_id, role='user', content=user_message, ear_num_context=ear_num_context)
    model_entry = ChatHistory(user_id=user_id, session_id=session_id, role='model', content=model_reply, ear_num_context=ear_num_context)
    db.session.add(user_entry)
    db.session.add(model_entry)
    db.session.commit()

# --- Dashboard (儀表板) 服務 ---
def get_dashboard_data(user_id):
    reminders = []
    today = date.today()
    seven_days_later = today + timedelta(days=7)
    user_sheep_query = Sheep.query.filter_by(user_id=user_id)
    reminder_fields = { "next_vaccination_due_date": "疫苗接種", "next_deworming_due_date": "驅蟲", "expected_lambing_date": "預產期" }
    for field, desc in reminder_fields.items():
        field_attr = getattr(Sheep, field)
        overdue_sheep = user_sheep_query.filter(field_attr != None, field_attr < today.strftime('%Y-%m-%d')).all()
        for s in overdue_sheep: reminders.append({"ear_num": s.EarNum, "type": desc, "due_date": getattr(s, field), "status": "已過期"})
        upcoming_sheep = user_sheep_query.filter(field_attr >= today.strftime('%Y-%m-%d'), field_attr <= seven_days_later.strftime('%Y-%m-%d')).all()
        for s in upcoming_sheep: reminders.append({"ear_num": s.EarNum, "type": desc, "due_date": getattr(s, field), "status": "即將到期"})
    flock_status_summary = db.session.query(Sheep.status, db.func.count(Sheep.status)).filter(Sheep.user_id == user_id, Sheep.status != None, Sheep.status != '').group_by(Sheep.status).all()
    flock_summary_list = [{"status": status, "count": count} for status, count in flock_status_summary]
    health_alerts = []
    user_sheep = user_sheep_query.all()
    thirty_days_ago = today - timedelta(days=30)
    for sheep in user_sheep:
        recent_weights = SheepHistoricalData.query.filter(SheepHistoricalData.sheep_id == sheep.id, SheepHistoricalData.record_type == 'Body_Weight_kg',).order_by(SheepHistoricalData.record_date.desc()).limit(2).all()
        if len(recent_weights) == 2:
            latest, prev = recent_weights[0], recent_weights[1]
            if datetime.strptime(latest.record_date, '%Y-%m-%d').date() >= thirty_days_ago and latest.value < prev.value and prev.value > 0:
                decrease_perc = ((prev.value - latest.value) / prev.value) * 100
                if decrease_perc > 5: health_alerts.append({ "ear_num": sheep.EarNum, "type": "體重顯著下降", "message": f"從 {prev.value}kg ({prev.record_date}) 降至 {latest.value}kg ({latest.record_date})，降幅 {decrease_perc:.1f}%。" })
        if sheep.status and 'lactating' in sheep.status:
            recent_milks = SheepHistoricalData.query.filter(SheepHistoricalData.sheep_id == sheep.id, SheepHistoricalData.record_type == 'milk_yield_kg_day',).order_by(SheepHistoricalData.record_date.desc()).limit(2).all()
            if len(recent_milks) == 2:
                latest, prev = recent_milks[0], recent_milks[1]
                if datetime.strptime(latest.record_date, '%Y-%m-%d').date() >= thirty_days_ago and latest.value < prev.value and prev.value > 0:
                    decrease_perc = ((prev.value - latest.value) / prev.value) * 100
                    if decrease_perc > 15: health_alerts.append({ "ear_num": sheep.EarNum, "type": "產奶量驟降", "message": f"日產奶量從 {prev.value}kg ({prev.record_date}) 降至 {latest.value}kg ({latest.record_date})，降幅 {decrease_perc:.1f}%。" })
    return {
        "reminders": sorted(reminders, key=lambda x: (x["due_date"] or "9999-99-99", x["status"])),
        "health_alerts": health_alerts,
        "flock_status_summary": flock_summary_list
    }

# --- END OF FILE backend/app/services/sheep_service.py ---