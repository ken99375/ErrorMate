from flask import Flask
from flask_login import LoginManager
from config import config
from models import db, User
# ★追加1：.env読み込み用のライブラリをインポート
from dotenv import load_dotenv

# Blueprintのインポート
from Blueprints.main import main_bp
from Blueprints.auth import auth_bp
from Blueprints.step_card import step_card_bp
from Blueprints.help import help_bp
from Blueprints.personal import personal_bp
from Blueprints.share import share_bp
from Blueprints.api import api_bp
from Blueprints.admin import admin_bp

# ★追加2：ここで.envファイルを強制的に読み込む！
# これがないと、configが環境変数(DB情報)を見つけられません
load_dotenv()

application = Flask(__name__)

# 設定の読み込み
application.config.from_object(config['default'])

# 接続先確認（これで mysql+pymysql://... と表示されれば成功！）
print("--------------------------------------------------") 
print("★接続先:", application.config.get('SQLALCHEMY_DATABASE_URI')) 
print("--------------------------------------------------")

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
    # Cloud9用に、ポート8080 と ホスト0.0.0.0 を指定する
    application.run(debug=True, port=8080, host='0.0.0.0')