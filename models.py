from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

STATUS_STEP    = 'step'
STATUS_HELP    = 'help'
STATUS_PUBLIC  = 'public'
STATUS_DELETED = 'delete'

class User(UserMixin, db.Model):
    """ユーザテーブル (設計書: USER)"""
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(255), nullable=False)
    mail = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='student')

    # リレーションシップ（あると便利）
    cards = db.relationship('StepCard', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

    def get_id(self):
        return str(self.user_id)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)



card_tags = db.Table('card_tags',
    db.Column('card_id', db.Integer, db.ForeignKey('step_cards.card_id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.tag_id'), primary_key=True)
)

class StepCard(db.Model):
    """ステップカードテーブル (設計書: CARD)"""
    __tablename__ = 'step_cards'

    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    error_code = db.Column(db.Text)         # エラーコード
    error_message = db.Column(db.Text)      # エラーメッセージ
    modifying_code = db.Column(db.Text) # 修正コード 
    execution_result = db.Column(db.Text)   # 実行結果 
    evaluation = db.Column(db.Integer, default=0) # 評価数
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    status = db.Column(db.String(50), nullable=False, default=STATUS_STEP, index=True)


    # タグとのリレーション
    tags = db.relationship('Tag', secondary=card_tags, lazy='subquery',
                        backref=db.backref('step_cards', lazy=True))
    # コメントとのリレーション
    comments = db.relationship('Comment', backref='card', lazy=True)




class Comment(db.Model):
    """コメントテーブル (設計書: COMMENT)"""
    __tablename__ = 'comments'

    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id = db.Column(db.Integer, db.ForeignKey('step_cards.card_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    body = db.Column(db.Text, nullable=False) # コメント本文
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

class Tag(db.Model):
    """タグテーブル (設計書: TAG)"""
    __tablename__ = 'tags'

    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_name = db.Column(db.String(100), nullable=False, unique=True) # 設計書に合わせて100に変更
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

class HelpCard(db.Model):
    """ヘルプカードテーブル (設計書: HELPCARD)"""
    __tablename__ = 'help_cards'

    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    title = db.Column(db.String(255), nullable=False)            # エラータイトル
    error_code = db.Column(db.Text)                              # エラーコード
    error_message = db.Column(db.Text)                           # エラーメッセージ
    tags = db.Column(db.String(200))                             # タグ（カンマ区切り）
    target = db.Column(db.String(50))                            # 投稿先（教師 or 学生）

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.String(50), default='help')            # 状態（help固定）
