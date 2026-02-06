from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from extensions import db
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import synonym
from werkzeug.security import generate_password_hash, check_password_hash

STATUS_STEP    = 'step'
STATUS_HELP    = 'help'
STATUS_PUBLIC  = 'public'
STATUS_DELETED = 'delete'


from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from extensions import db
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import synonym
from werkzeug.security import generate_password_hash, check_password_hash

STATUS_STEP    = 'step'
STATUS_HELP    = 'help'
STATUS_PUBLIC  = 'public'
STATUS_DELETED = 'delete'

class User(UserMixin, db.Model):
    """ユーザテーブル (設計書: USER)"""
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    moodle_user_id = db.Column(db.Integer, unique=True, nullable=True, index=True)
    username = db.Column(db.String(100), nullable=True, index=True)
    mail = db.Column(db.String(255), nullable=False, index=True)
    role = db.Column(db.String(50), nullable=True)

    # ★追加：パスワード（卒制用：平文で保存する運用）
    # DB側は password_hash カラムが既にあるのでそれに合わせる
    password_hash = db.Column(db.String(255), nullable=True)

    # 互換：過去コードの user_name を username に寄せる（DBカラムは増えない）
    user_name = synonym("username")

    # もし「password」という名前で扱いたいなら（任意）
    # password = synonym("password_hash")

    # リレーションシップ
    cards = db.relationship('StepCard', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

    def get_id(self):
        return str(self.user_id)

    @property
    def display_name(self) -> str:
        """表示用の名前。username が無ければ mail の@前を返す"""
        if self.username:
            return self.username
        if self.mail and "@" in self.mail:
            return self.mail.split("@")[0]
        return f"user{self.user_id}"

    # ★追加：パスワード設定/照合（卒制用の簡易版）
    def set_password(self, password: str) -> None:
        self.password_hash = password

    def check_password(self, password: str) -> bool:
        return (self.password_hash or "") == (password or "")

    # 互換：旧authが verify_password() を呼んでもOKにする
    def verify_password(self, password: str) -> bool:
        return self.check_password(password)



# ステップカードとタグの中間テーブル
card_tags = db.Table(
    'card_tags',
    db.Column('card_id', db.Integer, db.ForeignKey('step_cards.card_id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.tag_id'), primary_key=True)
)


class StepCard(db.Model):
    """ステップカードテーブル (設計書: CARD)"""
    __tablename__ = 'step_cards'

    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    error_code = db.Column(db.Text)
    error_message = db.Column(db.Text)
    modifying_code = db.Column(db.Text)
    execution_result = db.Column(db.Text)
    evaluation = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    status = db.Column(db.String(50), nullable=False, default=STATUS_STEP, index=True)

    tags = db.relationship(
        'Tag',
        secondary=card_tags,
        lazy='subquery',
        backref=db.backref('step_cards', lazy=True)
    )
    comments = db.relationship('Comment', backref='card', lazy=True)


class Comment(db.Model):
    """コメントテーブル (設計書: COMMENT)"""
    __tablename__ = 'comments'

    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id = db.Column(db.Integer, db.ForeignKey('step_cards.card_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # 親コメント（NULL ならルート）
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.comment_id'), nullable=True)

    # 便利リレーション
    parent = db.relationship('Comment', remote_side=[comment_id], backref='replies', lazy='select')


class Tag(db.Model):
    """タグテーブル (設計書: TAG)"""
    __tablename__ = 'tags'

    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)


class CardLike(db.Model):
    __tablename__ = 'likes'

    like_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_id = db.Column(db.Integer, db.ForeignKey('step_cards.card_id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('card_id', 'user_id', name='uix_like_card_user'),
    )

