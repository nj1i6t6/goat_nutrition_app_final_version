# --- START OF FILE backend/app/models.py ---

from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    """
    使用者模型，儲存使用者帳號資訊。
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # 關聯：一個使用者可以擁有多筆羊隻、事件等資料
    # cascade="all, delete-orphan" 表示刪除使用者時，其所有關聯資料也將一併刪除
    sheep = db.relationship('Sheep', backref='owner', lazy='dynamic', cascade="all, delete-orphan")
    events = db.relationship('SheepEvent', backref='owner', lazy='dynamic', cascade="all, delete-orphan")
    chat_history = db.relationship('ChatHistory', backref='owner', lazy='dynamic', cascade="all, delete-orphan")
    event_type_options = db.relationship('EventTypeOption', backref='owner', lazy='dynamic', cascade="all, delete-orphan")
    event_description_options = db.relationship('EventDescriptionOption', backref='owner', lazy='dynamic', cascade="all, delete-orphan")
    historical_data = db.relationship('SheepHistoricalData', backref='owner', lazy='dynamic', cascade="all, delete-orphan")

    def set_password(self, password):
        """設定使用者密碼，儲存為 hash 值。"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """核對輸入的密碼是否正確。"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login 需要的回呼函數，用來根據 user_id 重新載入使用者物件。"""
    return User.query.get(int(user_id))

class EventTypeOption(db.Model):
    """
    儲存使用者自訂的事件類型選項。
    """
    __tablename__ = 'event_type_option'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    
    descriptions = db.relationship('EventDescriptionOption', backref='event_type', lazy='dynamic', cascade="all, delete-orphan")

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'is_default': self.is_default}

class EventDescriptionOption(db.Model):
    """
    儲存使用者自訂的事件簡要描述選項，與 EventTypeOption 關聯。
    """
    __tablename__ = 'event_description_option'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_type_option_id = db.Column(db.Integer, db.ForeignKey('event_type_option.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    is_default = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            'id': self.id, 'event_type_option_id': self.event_type_option_id,
            'description': self.description, 'is_default': self.is_default
        }

class Sheep(db.Model):
    """
    羊隻核心資料模型。
    """
    __tablename__ = 'sheep'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 核心識別資料
    EarNum = db.Column(db.String(100), nullable=False)
    BirthDate = db.Column(db.String(50))
    Sex = db.Column(db.String(20))
    Breed = db.Column(db.String(100))
    
    # 血統資料
    Sire = db.Column(db.String(100))
    Dam = db.Column(db.String(100))
    
    # 從 Excel _Basic 工作表擴充的欄位
    BirWei = db.Column(db.Float)
    SireBre = db.Column(db.String(100))
    DamBre = db.Column(db.String(100))
    MoveCau = db.Column(db.String(100))
    MoveDate = db.Column(db.String(50))
    Class = db.Column(db.String(100))
    LittleSize = db.Column(db.Integer)
    Lactation = db.Column(db.Integer)
    ManaClas = db.Column(db.String(100))
    FarmNum = db.Column(db.String(100))
    RUni = db.Column(db.String(100))

    # 飼養管理與生產性能資料
    Body_Weight_kg = db.Column(db.Float)
    Age_Months = db.Column(db.Integer)
    breed_category = db.Column(db.String(50))
    status = db.Column(db.String(100))
    status_description = db.Column(db.Text)
    target_average_daily_gain_g = db.Column(db.Float)
    milk_yield_kg_day = db.Column(db.Float)
    milk_fat_percentage = db.Column(db.Float)
    number_of_fetuses = db.Column(db.Integer)
    expected_fiber_yield_g_day = db.Column(db.Float)
    activity_level = db.Column(db.String(100))
    
    # 備註與提醒
    other_remarks = db.Column(db.Text)
    agent_notes = db.Column(db.Text)
    next_vaccination_due_date = db.Column(db.String(50))
    next_deworming_due_date = db.Column(db.String(50))
    expected_lambing_date = db.Column(db.String(50))
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 同一使用者下的耳號必須是唯一的
    __table_args__ = (db.UniqueConstraint('user_id', 'EarNum', name='_user_ear_num_uc'),)
    
    # 關聯：一隻羊可以有多筆歷史數據和事件記錄
    historical_data = db.relationship('SheepHistoricalData', backref='sheep', lazy='dynamic', cascade="all, delete-orphan")
    events = db.relationship('SheepEvent', backref='sheep', lazy='dynamic', cascade="all, delete-orphan")

    def to_dict(self):
        """將模型物件轉換為字典，方便轉為 JSON。"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<Sheep {self.EarNum} OwnerID:{self.user_id}>'

class SheepEvent(db.Model):
    """
    羊隻事件日誌模型。
    """
    __tablename__ = 'sheep_event'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sheep_id = db.Column(db.Integer, db.ForeignKey('sheep.id', ondelete='CASCADE'), nullable=False)

    event_date = db.Column(db.String(50), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<Event {self.event_type} for SheepID:{self.sheep_id}>'
        
class SheepHistoricalData(db.Model):
    """
    儲存羊隻的歷史數值數據（如體重、產奶量）。
    """
    __tablename__ = 'sheep_historical_data'
    id = db.Column(db.Integer, primary_key=True)
    sheep_id = db.Column(db.Integer, db.ForeignKey('sheep.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    record_date = db.Column(db.String(50), nullable=False)
    record_type = db.Column(db.String(100), nullable=False) # e.g., 'Body_Weight_kg'
    value = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<HistoricalData {self.record_type}:{self.value} for SheepID:{self.sheep_id}>'

class ChatHistory(db.Model):
    """
    AI 聊天歷史記錄模型。
    """
    __tablename__ = 'chat_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'user' or 'model'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ear_num_context = db.Column(db.String(100)) # 聊天時針對的羊隻耳號
    
    def __repr__(self):
        return f'<Chat {self.session_id} - {self.role}>'

# --- END OF FILE backend/app/models.py ---