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
from Blueprints.share import share_bp
from Blueprints.api import api_bp
from Blueprints.admin import admin_bp


application = Flask(__name__)

# 設定の読み込み
application.config.from_object(config['default'])

# データベースの初期化
db.init_app(application)

# ログインマネージャーの初期化
login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Blueprintの登録
application.register_blueprint(main_bp)

application.register_blueprint(step_card_bp, url_prefix='/card')

application.register_blueprint(auth_bp, url_prefix='/auth')

application.register_blueprint(help_bp, url_prefix='/help')

application.register_blueprint(personal_bp, url_prefix='/personal')

application.register_blueprint(share_bp, url_prefix='/share')

application.register_blueprint(api_bp, url_prefix="/api")

application.register_blueprint(admin_bp, url_prefix='/admin')

# アプリ起動時にテーブルを作成
with application.app_context():
    db.create_all()

if __name__ == '__main__':
    application.run(debug=True)