from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# SQLAlchemyのインスタンスを作成（まだアプリと紐付けない）
db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    ユーザーテーブルのモデル
    UserMixinを継承することで、Flask-Loginが必要とするメソッド
    (is_authenticated, get_idなど)が自動で追加される
    """
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(255), nullable=False)
    mail = db.Column(db.String(50), nullable=False, unique=True) # メールアドレスは重複不可に設定
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    password_hash = db.Column(db.String(255), nullable=False) # パスワードはハッシュ化して保存
    role = db.Column(db.String(50), nullable=False, default='student') # デフォルトは学生

    # Flask-LoginがユーザーIDを取得する際に呼ぶメソッドをオーバーライド
    def get_id(self):
        return str(self.user_id)

    # パスワードをセットするときに自動でハッシュ化するプロパティ
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # 入力されたパスワードが正しいかチェックするメソッド
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)