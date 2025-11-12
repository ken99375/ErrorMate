from flask import Flask
from flask_login import LoginManager
from config import config
from models import db, User

# Blueprintのインポート
from Blueprints.main import main_bp
from Blueprints.auth import auth_bp
from Blueprints.step_card import step_card_bp
from Blueprints.help import help_bp
from Blueprints.personal import personal_bp



app = Flask(__name__)

# 設定の読み込み
app.config.from_object(config['default'])

# データベースの初期化
db.init_app(app)

# ログインマネージャーの初期化
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Blueprintの登録
app.register_blueprint(main_bp)

app.register_blueprint(step_card_bp, url_prefix='/card')

app.register_blueprint(auth_bp, url_prefix='/auth')

app.register_blueprint(help_bp, url_prefix='/help')

app.register_blueprint(personal_bp, url_prefix='/personal')

# アプリ起動時にテーブルを作成
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()