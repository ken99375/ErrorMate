from flask import Flask, request, session, redirect, url_for
from flask_login import LoginManager, login_user
from config import config
from models import db, User
# ★追加1：.env読み込み用のライブラリをインポート
from dotenv import load_dotenv
from datetime import timezone
from zoneinfo import ZoneInfo

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

# Moodleから ?username=xxx で来た人を受け取る場所
@application.route('/auto_login')
def auto_login():
    # 1. URLから ?username= の中身（例: tada）を取り出す
    username_from_url = request.args.get('username')
    
    # 2. その名前のユーザーがデータベースにいるか探す
    # (※あなたのDBのカラム名が 'name' なのか 'username' なのか 'email' なのかに合わせて変更してください)
    user = User.query.filter_by(username=username_from_url).first() 

    if user:
        # 3. ★ここが一番重要！★ そのユーザーとしてログイン状態にする
        login_user(user)
        
        # 4. ログイン成功！トップページへ
        return redirect(url_for('index'))
        
    else:
        # ユーザーが見つからなかった場合のエラー表示
        return f"エラー: '{username_from_url}' というユーザーが見つかりません。"
    
@application.template_filter('jst')
def jst(dt):
    if not dt:
        return ''
    # DBにnaive(タイムゾーンなし)でUTC保存してる想定
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    # 表示だけJSTに
    return dt.astimezone(ZoneInfo("Asia/Tokyo")).strftime('%Y-%m-%d %H:%M')

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