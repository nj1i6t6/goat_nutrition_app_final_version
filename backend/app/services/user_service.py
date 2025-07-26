# --- START OF FILE backend/app/services/user_service.py ---

from .. import db
from ..models import User, EventTypeOption, EventDescriptionOption

def create_user_with_defaults(username, password):
    """
    創建一個新使用者，並為其初始化一組預設的事件選項。
    這是一個完整的交易，要麼全部成功，要麼全部回滾。

    Args:
        username (str): 使用者名稱。
        password (str): 使用者密碼。

    Returns:
        User: 新創建的使用者物件。

    Raises:
        ValueError: 如果使用者名稱已存在或輸入無效。
        Exception: 如果資料庫操作失敗。
    """
    if not username or not password:
        raise ValueError('使用者名稱和密碼為必填項')
    
    if User.query.filter_by(username=username).first():
        raise ValueError('此使用者名稱已被註冊')

    try:
        # 1. 創建使用者
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        
        # 2. Flush a session: 將變更寫入資料庫事務，以便獲取 new_user.id
        # 這一步是關鍵，它讓 user 物件在 commit 之前就擁有了 id
        db.session.flush()

        # 3. 為新使用者創建預設事件選項
        _create_default_event_options(new_user)
        
        # 4. 提交整個事務
        db.session.commit()
        
        return new_user
    except Exception as e:
        # 如果任何步驟失敗，回滾所有變更
        db.session.rollback()
        # 記錄錯誤日誌會更好，這裡我們先拋出異常
        raise Exception(f"創建使用者時發生錯誤: {e}")

def authenticate_user(username, password):
    """
    驗證使用者身份。

    Args:
        username (str): 使用者名稱。
        password (str): 密碼。

    Returns:
        User or None: 如果驗證成功，返回使用者物件；否則返回 None。
    """
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None

def get_all_event_options(user_id):
    """
    獲取指定使用者的所有事件類型及對應的描述選項。
    """
    types = EventTypeOption.query.filter_by(user_id=user_id).order_by(EventTypeOption.is_default.desc(), EventTypeOption.name).all()
    options_data = []
    for type_option in types:
        descriptions = [desc.to_dict() for desc in type_option.descriptions.order_by(EventDescriptionOption.is_default.desc(), EventDescriptionOption.description).all()]
        type_dict = type_option.to_dict()
        type_dict['descriptions'] = descriptions
        options_data.append(type_dict)
    return options_data

def add_event_type(user_id, name):
    """為使用者新增一個事件類型。"""
    if EventTypeOption.query.filter_by(user_id=user_id, name=name).first():
        raise ValueError(f"類型 '{name}' 已存在")
    
    new_type = EventTypeOption(user_id=user_id, name=name, is_default=False)
    db.session.add(new_type)
    db.session.commit()
    return new_type.to_dict()

def delete_event_type(user_id, option_id):
    """刪除使用者自訂的事件類型。"""
    option = EventTypeOption.query.filter_by(id=option_id, user_id=user_id).first_or_404()
    if option.is_default:
        raise ValueError("不能刪除預設的事件類型")
    
    db.session.delete(option)
    db.session.commit()

def add_event_description(user_id, type_id, description_text):
    """為指定的事件類型新增一個簡要描述。"""
    parent_type = EventTypeOption.query.filter_by(id=type_id, user_id=user_id).first_or_404()
    if EventDescriptionOption.query.filter_by(event_type_option_id=type_id, description=description_text).first():
        raise ValueError(f"描述 '{description_text}' 已存在於此類型中")
        
    new_desc = EventDescriptionOption(
        user_id=user_id,
        event_type_option_id=parent_type.id,
        description=description_text,
        is_default=False
    )
    db.session.add(new_desc)
    db.session.commit()
    return new_desc.to_dict()

def delete_event_description(user_id, option_id):
    """刪除使用者自訂的事件簡要描述。"""
    option = EventDescriptionOption.query.filter_by(id=option_id, user_id=user_id).first_or_404()
    if option.is_default:
        raise ValueError("不能刪除預設的簡要描述")
        
    db.session.delete(option)
    db.session.commit()

# --- Private Helper Functions ---

def _create_default_event_options(user):
    """
    (私有) 為新使用者創建一套預設的事件類型和描述選項。
    這個函數假設它在一個更大的資料庫事務中被調用。
    """
    default_options = {
        "疫苗接種": ["口蹄疫疫苗", "炭疽病疫苗", "破傷風類毒素"],
        "疾病治療": ["盤尼西林注射", "抗生素治療", "消炎藥"],
        "配種": ["自然配種", "人工授精"],
        "產仔": ["單胎", "雙胎", "三胎以上"],
        "體重記錄": [],
        "飼料調整": ["更換精料", "增加草料", "補充礦物質"],
        "驅蟲": ["內寄生蟲 (口服)", "外寄生蟲 (噴灑)"],
        "特殊觀察": ["食慾不振", "跛行", "精神沉鬱"],
        "AI飼養建議諮詢": [],
        "其他": []
    }
    
    for type_name, descriptions in default_options.items():
        event_type = EventTypeOption(user_id=user.id, name=type_name, is_default=True)
        db.session.add(event_type)
        db.session.flush() # 獲取 event_type.id
        
        for desc_text in descriptions:
            description = EventDescriptionOption(
                user_id=user.id,
                event_type_option_id=event_type.id,
                description=desc_text,
                is_default=True
            )
            db.session.add(description)

# --- END OF FILE backend/app/services/user_service.py ---